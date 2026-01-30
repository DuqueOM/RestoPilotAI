import { useEffect, useState } from 'react';

export interface PeriodInfo {
  available: boolean;
  label: string;
  records: number;
  coverage_pct: number;
  days_required: number | null;
  reason?: string;
}

export interface AvailablePeriodsData {
  available_periods: string[];
  data_span_days: number;
  earliest_date: string;
  latest_date: string;
  total_records: number;
  period_info: Record<string, PeriodInfo>;
}

export function useAvailablePeriods(sessionData: any): AvailablePeriodsData | null {
  const [periodsData, setPeriodsData] = useState<AvailablePeriodsData | null>(null);

  useEffect(() => {
    if (sessionData?.available_periods) {
      setPeriodsData(sessionData.available_periods);
    }
  }, [sessionData]);

  return periodsData;
}

export function filterValidPeriods(
  allPeriods: Array<{ id: string; label: string; description?: string }>,
  availablePeriodsData: AvailablePeriodsData | null
): Array<{ id: string; label: string; description?: string; available: boolean }> {
  if (!availablePeriodsData) {
    return allPeriods.map(p => ({ ...p, available: true }));
  }

  return allPeriods.map(period => ({
    ...period,
    available: availablePeriodsData.available_periods.includes(period.id),
  }));
}
