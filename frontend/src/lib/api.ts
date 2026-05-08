const LOCAL_API_ORIGIN = "http://localhost:8080";

export function apiUrl(path: `/${string}`): string {
  if (typeof window !== "undefined" && window.location.hostname === "localhost") {
    return `${LOCAL_API_ORIGIN}${path}`;
  }

  return path;
}
