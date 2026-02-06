'use client';

import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCcw } from 'lucide-react';
import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-center px-4">
      <div className="bg-red-50 p-4 rounded-full shadow-sm mb-6 border border-red-100">
        <AlertTriangle className="h-12 w-12 text-red-600" />
      </div>
      <h2 className="text-3xl font-bold text-gray-900 mb-2">Something went wrong</h2>
      <p className="text-gray-600 mb-8 max-w-md">
        An unexpected error occurred. Please try again.
      </p>
      <Button onClick={reset} variant="outline" className="gap-2">
        <RefreshCcw className="h-4 w-4" />
        Try again
      </Button>
    </div>
  );
}
