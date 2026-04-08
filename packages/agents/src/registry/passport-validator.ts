import { AgentPassport } from './passport.js';

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export function validatePassportDetails(passport: AgentPassport): ValidationResult {
  const errors: string[] = [];

  // 1. Check maturity rules
  const maturity = passport.maturityLevel();
  if (['L3', 'L4', 'L5'].includes(maturity)) {
    if (!passport.data.kill_switch.enabled) {
      errors.push(`Maturity level ${maturity} requires a functional kill_switch.enabled = true`);
    }
  }

  // 2. Check S16 logic
  if (passport.isRetired() && passport.data.kill_switch.active !== true) {
    errors.push(`Retired (S16) agents should generally have kill_switch.active = true`);
  }

  // 3. Owners must exist
  if (!passport.data.owners || passport.data.owners.length === 0) {
    errors.push(`Agent must specify at least one owner email`);
  }

  return {
    valid: errors.length === 0,
    errors
  };
}
