import { RealApiError } from "@/services/realApiClient";

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (!(error instanceof RealApiError)) return fallback;

  switch (error.status) {
    case 401:
      return "Votre session a expiré. Reconnectez-vous pour continuer.";
    case 403:
      return "Vous n’avez pas accès à ce livre.";
    case 404:
      return "Ce livre n’existe plus ou n’est plus disponible.";
    case 409:
      return "Cette modification est devenue obsolète. Rechargez les données avant de réessayer.";
    default:
      return error.message || fallback;
  }
}
