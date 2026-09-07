import { api } from './api';
import { Shift, Attendance, AttendanceSummary } from '../types/attendance';

export const attendanceService = {
  getShifts: async (companyId: number = 1): Promise<Shift[]> => {
    const res = await api.get<Shift[]>(`/attendance/shifts?company_id=${companyId}`);
    return res.data;
  },

  createShift: async (data: Partial<Shift>): Promise<Shift> => {
    const res = await api.post<Shift>('/attendance/shifts', data);
    return res.data;
  },

  checkIn: async (employeeId: number, checkInTime: string, date: string): Promise<Attendance> => {
    const res = await api.post<Attendance>('/attendance/check-in', {
      employee_id: employeeId,
      date,
      check_in_time: checkInTime,
    });
    return res.data;
  },

  checkOut: async (employeeId: number, checkOutTime: string, date: string): Promise<Attendance> => {
    const res = await api.post<Attendance>('/attendance/check-out', {
      employee_id: employeeId,
      date,
      check_out_time: checkOutTime,
    });
    return res.data;
  },

  getAttendanceRecords: async (employeeId?: number, startDate?: string, endDate?: string): Promise<Attendance[]> => {
    const res = await api.get<Attendance[]>('/attendance', {
      params: { employee_id: employeeId, start_date: startDate, end_date: endDate },
    });
    return res.data;
  },

  getAttendanceSummary: async (employeeId: number, yearMonth: string): Promise<AttendanceSummary> => {
    const res = await api.get<AttendanceSummary>('/attendance/summary', {
      params: { employee_id: employeeId, year_month: yearMonth },
    });
    return res.data;
  },
};
