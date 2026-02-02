'use client';

import { CreativeStudio } from '@/components/dashboard/CreativeStudio';
import { useParams } from 'next/navigation';

export default function CreativePage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  return (
    <div className="space-y-6">
      <CreativeStudio sessionId={sessionId} />
    </div>
  );
}
