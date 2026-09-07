export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface CurrentUserPermissions {
  id: number;
  uuid: string;
  email: string;
  full_name: string;
  is_superuser: boolean;
  roles: string[];
  permissions: string[];
}
