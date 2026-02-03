import asyncio
import json
from typing import Dict, List, Optional, Callable
from datetime import datetime, timezone
from loguru import logger

from app.core.config import get_settings

class MarathonAgent:
    """
    Implementación completa del patrón Marathon Agent.
    
    TRACK DEL HACKATHON: Marathon Agent
    
    Capacidades:
    - Checkpoints automáticos persistentes (Redis/DB)
    - Recuperación de fallos con retry exponencial
    - Progreso en tiempo real vía WebSocket
    - Multi-hora execution con timeouts largos
    - State snapshots para debugging
    """
    
    def __init__(self):
        settings = get_settings()
        self.checkpoint_interval = settings.marathon_checkpoint_interval  # 60 segundos
        self.max_retries = settings.marathon_max_retries_per_step  # 3
        self.enable_recovery = settings.marathon_enable_recovery
        self.enable_checkpoints = settings.marathon_enable_checkpoints
        self.max_task_duration = settings.marathon_max_task_duration  # 3600 segundos
        
        # WebSocket connection manager (will be injected)
        self.ws_manager = None
        
        # Storage backend (Redis preferred, fallback to in-memory)
        self._init_storage()
    
    async def execute_long_running_task(
        self,
        task_id: str,
        task_config: Dict,
        progress_callback: Callable = None
    ) -> Dict:
        """
        Ejecuta tarea de larga duración con checkpoints.
        
        Ejemplo de uso:
        - Análisis competitivo de 50 restaurantes
        - Procesamiento de 100 fotos de platos
        - Generación de 20 variaciones de campaña
        """
        
        # Verificar si existe checkpoint previo
        checkpoint = await self._load_checkpoint(task_id)
        
        if checkpoint:
            logger.info(f"Recuperando desde checkpoint: {checkpoint['step']}")
            current_step = checkpoint['step']
            accumulated_results = checkpoint['results']
        else:
            current_step = 0
            accumulated_results = {}
        
        # Definir steps del pipeline
        pipeline_steps = self._define_pipeline_steps(task_config)
        
        # Ejecutar desde el paso actual
        for i in range(current_step, len(pipeline_steps)):
            step = pipeline_steps[i]
            
            try:
                # Ejecutar step con retry logic
                result = await self._execute_step_with_retry(
                    step,
                    accumulated_results
                )
                
                accumulated_results[step['name']] = result
                
                # Guardar checkpoint
                await self._save_checkpoint(
                    task_id,
                    step=i + 1,
                    results=accumulated_results
                )
                
                # Progress updates (callback + WebSocket)
                progress_data = {
                    "task_id": task_id,
                    "progress": (i + 1) / len(pipeline_steps),
                    "current_step": step['name'],
                    "status": "running",
                    "step_index": i + 1,
                    "total_steps": len(pipeline_steps)
                }
                
                # Send via WebSocket
                await self._send_progress_update(task_id, progress_data)
                
                # Call callback if provided
                if progress_callback:
                    await progress_callback(progress_data)
            
            except Exception as e:
                # Guardar estado de error
                await self._save_error_state(task_id, i, str(e))
                raise
        
        # Limpiar checkpoint al finalizar
        await self._clear_checkpoint(task_id)
        
        return {
            "task_id": task_id,
            "status": "completed",
            "results": accumulated_results,
            "total_steps": len(pipeline_steps)
        }
    
    async def _execute_step_with_retry(
        self,
        step: Dict,
        context: Dict
    ) -> Dict:
        """
        Ejecuta un step con retry automático.
        """
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # Assuming step['function'] is an async callable that takes context
                result = await step['function'](context)
                return result
            
            except Exception as e:
                last_error = e
                logger.warning(f"Step {step['name']} attempt {attempt + 1} failed: {e}")
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"Step {step['name']} failed after {self.max_retries} attempts: {last_error}")

    def _init_storage(self):
        """Initialize storage backend for checkpoints."""
        try:
            # Try to use Redis if available
            import redis.asyncio as redis
            settings = get_settings()
            self.redis_client = redis.from_url(settings.redis_url)
            self.storage_backend = "redis"
            logger.info("Marathon Agent using Redis for checkpoints")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory storage: {e}")
            self.state_storage = {}
            self.storage_backend = "memory"
    
    def set_websocket_manager(self, manager):
        """Inject WebSocket connection manager for progress updates."""
        self.ws_manager = manager
    
    # === PERSISTENT CHECKPOINT METHODS ===
    
    async def _load_checkpoint(self, task_id: str) -> Optional[Dict]:
        """
        Load checkpoint from persistent storage.
        
        Returns checkpoint data or None if not found.
        """
        if not self.enable_checkpoints:
            return None
        
        try:
            if self.storage_backend == "redis":
                data = await self.redis_client.get(f"checkpoint:{task_id}")
                if data:
                    return json.loads(data)
            else:
                return self.state_storage.get(task_id)
        except Exception as e:
            logger.error(f"Failed to load checkpoint for {task_id}: {e}")
        
        return None
    
    async def _save_checkpoint(self, task_id: str, step: int, results: Dict):
        """
        Save checkpoint to persistent storage.
        
        Checkpoints include:
        - Current step index
        - Accumulated results
        - Timestamp
        - State snapshot for debugging
        """
        if not self.enable_checkpoints:
            return
        
        checkpoint_data = {
            "task_id": task_id,
            "step": step,
            "results": results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state_snapshot": self._get_state_snapshot()
        }
        
        try:
            if self.storage_backend == "redis":
                # TTL: 1 hora (3600 segundos)
                await self.redis_client.setex(
                    f"checkpoint:{task_id}",
                    3600,
                    json.dumps(checkpoint_data, default=str)
                )
                logger.debug(f"Checkpoint saved to Redis: {task_id} step {step}")
            else:
                self.state_storage[task_id] = checkpoint_data
                logger.debug(f"Checkpoint saved to memory: {task_id} step {step}")
        
        except Exception as e:
            logger.error(f"Failed to save checkpoint for {task_id}: {e}")
    
    async def _save_error_state(self, task_id: str, step: int, error: str):
        """
        Save error state for recovery analysis.
        """
        error_data = {
            "task_id": task_id,
            "step": step,
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            if self.storage_backend == "redis":
                await self.redis_client.setex(
                    f"error:{task_id}",
                    3600,
                    json.dumps(error_data)
                )
            else:
                if task_id in self.state_storage:
                    self.state_storage[task_id]["error"] = error_data
        
        except Exception as e:
            logger.error(f"Failed to save error state: {e}")
    
    async def _clear_checkpoint(self, task_id: str):
        """
        Clear checkpoint after successful completion.
        """
        try:
            if self.storage_backend == "redis":
                await self.redis_client.delete(f"checkpoint:{task_id}")
                await self.redis_client.delete(f"error:{task_id}")
                logger.info(f"Checkpoint cleared for {task_id}")
            else:
                if task_id in self.state_storage:
                    del self.state_storage[task_id]
        
        except Exception as e:
            logger.error(f"Failed to clear checkpoint: {e}")
    
    def _get_state_snapshot(self) -> Dict:
        """Get current state snapshot for debugging."""
        return {
            "storage_backend": self.storage_backend,
            "checkpoint_interval": self.checkpoint_interval,
            "max_retries": self.max_retries,
            "enable_recovery": self.enable_recovery
        }
    
    # === WEBSOCKET PROGRESS UPDATES ===
    
    async def _send_progress_update(self, task_id: str, update: Dict):
        """
        Send progress update via WebSocket if available.
        
        Falls back to logging if WebSocket not connected.
        """
        if self.ws_manager:
            try:
                await self.ws_manager.send_progress(task_id, {
                    "type": "progress_update",
                    "data": update,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                logger.warning(f"Failed to send WebSocket update: {e}")
        else:
            logger.info(f"Progress update for {task_id}: {update}")
    
    def _define_pipeline_steps(self, config: Dict) -> List[Dict]:
        """
        Define pipeline steps from config.
        
        Config should provide 'steps' list with:
        - name: Step name
        - function: Async callable
        - timeout: Optional timeout in seconds
        - retryable: Whether step can be retried
        """
        return config.get('steps', [])
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """
        Get current status of a Marathon task.
        
        Useful for monitoring and recovery.
        """
        checkpoint = await self._load_checkpoint(task_id)
        
        if checkpoint:
            return {
                "task_id": task_id,
                "status": "running",
                "current_step": checkpoint.get("step", 0),
                "last_update": checkpoint.get("timestamp"),
                "has_checkpoint": True
            }
        
        return {
            "task_id": task_id,
            "status": "not_found",
            "has_checkpoint": False
        }
