import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function hasEnvVars(envVars: string[]): boolean {
  return envVars.every((envVar) => process.env[envVar]);
}
