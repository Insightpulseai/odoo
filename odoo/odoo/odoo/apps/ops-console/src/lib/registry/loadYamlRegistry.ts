import fs from 'fs'
import path from 'path'
import yaml from 'js-yaml'
import { REGISTRY_PATHS, resolveRegistryDir, type RegistryFamily } from './registryPaths'

export interface RegistryFile<T = Record<string, unknown>> {
  /** Relative path from repo root */
  filePath: string
  /** Parsed YAML content */
  data: T
  /** File modification time */
  mtime: Date
}

/**
 * Load all YAML files from a single directory.
 * Returns empty array if directory doesn't exist (not an error).
 */
export function loadYamlDir<T = Record<string, unknown>>(
  relativePath: string
): RegistryFile<T>[] {
  const absDir = resolveRegistryDir(relativePath)

  if (!fs.existsSync(absDir)) {
    console.warn(`[registry] Directory not found: ${relativePath}`)
    return []
  }

  const files = fs.readdirSync(absDir).filter(f => f.endsWith('.yaml') || f.endsWith('.yml'))
  const results: RegistryFile<T>[] = []

  for (const file of files) {
    const absPath = path.join(absDir, file)
    try {
      const raw = fs.readFileSync(absPath, 'utf-8')
      const data = yaml.load(raw) as T
      const stat = fs.statSync(absPath)
      results.push({
        filePath: path.join(relativePath, file),
        data,
        mtime: stat.mtime,
      })
    } catch (err) {
      console.error(`[registry] Failed to parse ${relativePath}/${file}:`, err)
      // Skip malformed files — don't crash the whole page
    }
  }

  return results
}

/**
 * Load all YAML files for a registry family (e.g., 'agents' loads from all agent dirs).
 */
export function loadRegistryFamily<T = Record<string, unknown>>(
  family: RegistryFamily
): RegistryFile<T>[] {
  const dirs = REGISTRY_PATHS[family]
  const allFiles: RegistryFile<T>[] = []

  for (const dir of dirs) {
    allFiles.push(...loadYamlDir<T>(dir))
  }

  return allFiles
}

/**
 * Load a single YAML file by relative path from repo root.
 * Returns null if file doesn't exist.
 */
export function loadYamlFile<T = Record<string, unknown>>(
  relativePath: string
): RegistryFile<T> | null {
  const absPath = resolveRegistryDir(relativePath)

  if (!fs.existsSync(absPath)) {
    console.warn(`[registry] File not found: ${relativePath}`)
    return null
  }

  try {
    const raw = fs.readFileSync(absPath, 'utf-8')
    const data = yaml.load(raw) as T
    const stat = fs.statSync(absPath)
    return { filePath: relativePath, data, mtime: stat.mtime }
  } catch (err) {
    console.error(`[registry] Failed to parse ${relativePath}:`, err)
    return null
  }
}
