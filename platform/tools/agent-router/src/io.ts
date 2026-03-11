import fs from "node:fs/promises";
import YAML from "yaml";

export async function readYamlFile<T>(filePath: string): Promise<T> {
  const raw = await fs.readFile(filePath, "utf8");
  return YAML.parse(raw) as T;
}

export async function readTextFile(filePath: string): Promise<string> {
  return await fs.readFile(filePath, "utf8");
}

export async function exists(filePath: string): Promise<boolean> {
  try {
    await fs.stat(filePath);
    return true;
  } catch {
    return false;
  }
}
