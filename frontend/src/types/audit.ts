export interface AuditLogRow {
  id: number;
  user_id?: number;
  user_email?: string;
  action: string;
  module: string;
  record_id?: string;
  old_values?: Record<string, any>;
  new_values?: Record<string, any>;
  ip_address?: string;
  hash_checksum?: string;
  created_at: string;
}

export interface AuditLogsResponse {
  total: number;
  offset: number;
  limit: number;
  logs: AuditLogRow[];
}

export interface AuditIntegrityResponse {
  is_intact: boolean;
  total_entries: number;
  tampered_entry_id?: number;
  reason?: string;
}
