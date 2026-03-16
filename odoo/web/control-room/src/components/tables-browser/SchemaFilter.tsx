'use client';

import { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { Check, ChevronDown, Database, Globe } from 'lucide-react';
import { DatabaseSchema } from '@/lib/supabase';
import clsx from 'clsx';

interface SchemaFilterProps {
  schemas: DatabaseSchema[];
  value: string;
  onChange: (value: string) => void;
  loading?: boolean;
}

export function SchemaFilter({
  schemas,
  value,
  onChange,
  loading,
}: SchemaFilterProps) {
  const exposedSchemas = schemas.filter((s) => s.is_exposed);
  const otherSchemas = schemas.filter((s) => !s.is_exposed);

  const selectedLabel =
    value === 'all'
      ? 'All Schemas'
      : value === 'exposed'
        ? 'Exposed Schemas'
        : value;

  return (
    <Listbox value={value} onChange={onChange} disabled={loading}>
      <div className="relative">
        <Listbox.Button
          className={clsx(
            'relative w-full min-w-[180px] cursor-pointer rounded-lg py-2 pl-3 pr-10 text-left',
            'bg-surface-800 border border-surface-600',
            'text-sm text-white',
            'focus:outline-none focus:ring-2 focus:ring-blue-500',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          <span className="flex items-center gap-2 truncate">
            <Database className="w-4 h-4 text-surface-400" />
            {selectedLabel}
          </span>
          <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronDown className="w-4 h-4 text-surface-400" />
          </span>
        </Listbox.Button>

        <Transition
          as={Fragment}
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <Listbox.Options
            className={clsx(
              'absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-lg py-1',
              'bg-surface-800 border border-surface-600 shadow-lg',
              'focus:outline-none'
            )}
          >
            {/* All Schemas */}
            <Listbox.Option
              value="all"
              className={({ active }) =>
                clsx(
                  'relative cursor-pointer select-none py-2 pl-10 pr-4 text-sm',
                  active ? 'bg-surface-700 text-white' : 'text-surface-200'
                )
              }
            >
              {({ selected }) => (
                <>
                  <span
                    className={clsx(
                      'block truncate',
                      selected ? 'font-medium text-white' : ''
                    )}
                  >
                    All Schemas
                  </span>
                  {selected && (
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-400">
                      <Check className="w-4 h-4" />
                    </span>
                  )}
                </>
              )}
            </Listbox.Option>

            {/* Exposed Schemas (virtual) */}
            <Listbox.Option
              value="exposed"
              className={({ active }) =>
                clsx(
                  'relative cursor-pointer select-none py-2 pl-10 pr-4 text-sm',
                  active ? 'bg-surface-700 text-white' : 'text-surface-200'
                )
              }
            >
              {({ selected }) => (
                <>
                  <span
                    className={clsx(
                      'flex items-center gap-2 truncate',
                      selected ? 'font-medium text-white' : ''
                    )}
                  >
                    <Globe className="w-3 h-3 text-emerald-400" />
                    Exposed Schemas
                  </span>
                  {selected && (
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-400">
                      <Check className="w-4 h-4" />
                    </span>
                  )}
                </>
              )}
            </Listbox.Option>

            {/* Divider */}
            <div className="my-1 border-t border-surface-600" />

            {/* Exposed schemas */}
            {exposedSchemas.length > 0 && (
              <>
                <div className="px-3 py-1 text-[10px] font-medium text-surface-400 uppercase tracking-wide">
                  Exposed
                </div>
                {exposedSchemas.map((schema) => (
                  <Listbox.Option
                    key={schema.schema_name}
                    value={schema.schema_name}
                    className={({ active }) =>
                      clsx(
                        'relative cursor-pointer select-none py-2 pl-10 pr-4 text-sm',
                        active ? 'bg-surface-700 text-white' : 'text-surface-200'
                      )
                    }
                  >
                    {({ selected }) => (
                      <>
                        <span
                          className={clsx(
                            'flex items-center justify-between truncate',
                            selected ? 'font-medium text-white' : ''
                          )}
                        >
                          {schema.schema_name}
                          <span className="text-xs text-surface-400">
                            {schema.table_count}
                          </span>
                        </span>
                        {selected && (
                          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-400">
                            <Check className="w-4 h-4" />
                          </span>
                        )}
                      </>
                    )}
                  </Listbox.Option>
                ))}
              </>
            )}

            {/* Other schemas */}
            {otherSchemas.length > 0 && (
              <>
                <div className="px-3 py-1 text-[10px] font-medium text-surface-400 uppercase tracking-wide mt-1">
                  Other
                </div>
                {otherSchemas.map((schema) => (
                  <Listbox.Option
                    key={schema.schema_name}
                    value={schema.schema_name}
                    className={({ active }) =>
                      clsx(
                        'relative cursor-pointer select-none py-2 pl-10 pr-4 text-sm',
                        active ? 'bg-surface-700 text-white' : 'text-surface-200'
                      )
                    }
                  >
                    {({ selected }) => (
                      <>
                        <span
                          className={clsx(
                            'flex items-center justify-between truncate',
                            selected ? 'font-medium text-white' : ''
                          )}
                        >
                          {schema.schema_name}
                          <span className="text-xs text-surface-400">
                            {schema.table_count}
                          </span>
                        </span>
                        {selected && (
                          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-blue-400">
                            <Check className="w-4 h-4" />
                          </span>
                        )}
                      </>
                    )}
                  </Listbox.Option>
                ))}
              </>
            )}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}
