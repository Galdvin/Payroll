export interface Shift {
  id: number;
  company_id: number;
  name: string;
  code: string;
  start_time: string;
  end_time: string;
  grace_period_minutes: number;
  break_duration_minutes: number;
  is_night_shift: boolean;
  overtime_start_after_minutes: number;
}

export interface Attendance {
  id: number;
  employee_id: number;
  date: string;
  check_in?: string;
  check_out?: string;
  status: string;
  late_minutes: number;
  early_departure_minutes: number;
  overtime_hours: number;
  source: string;
}

export interface AttendanceSummary {
  id: number;
  employee_id: number;
  year_month: string;
  total_days: number;
  present_days: number;
  absent_days: number;
  paid_leave_days: number;
  unpaid_leave_days: number;
  weekly_off_days: number;
  holiday_days: number;
  payable_days: number;
  overtime_hours: number;
}
