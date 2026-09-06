import { RealApiError } from "@/services/realApiClient";

const GENERIC_LOGIN_ERROR = "Adresse e-mail ou mot de passe incorrect.";
const RATE_LIMIT_ERROR = "Trop de tentatives. Attendez un peu avant de réessayer.";
const NETWORK_ERROR = "Le service est momentanément indisponible. Vérifiez votre connexion puis réessayez.";
const GENERIC_REGISTER_ERROR = "Impossible de créer le compte. Vérifiez les informations saisies et réessayez.";

export function getLoginError(error: unknown): string {
  if (error instanceof RealApiError) {
    if (error.status === 401 || error.status === 403) return GENERIC_LOGIN_ERROR;
    if (error.status === 429) return RATE_LIMIT_ERROR;
    if (error.status === null) return NETWORK_ERROR;
  }
  return GENERIC_LOGIN_ERROR;
}

export function getRegisterError(error: unknown): string {
  if (error instanceof RealApiError) {
    if (error.status === 429) return RATE_LIMIT_ERROR;
    if (error.status === 422) return error.message || "Vérifiez les informations saisies.";
    if (error.status === 400 || error.status === 409) return GENERIC_REGISTER_ERROR;
    if (error.status === null) return NETWORK_ERROR;
  }
  return GENERIC_REGISTER_ERROR;
}
