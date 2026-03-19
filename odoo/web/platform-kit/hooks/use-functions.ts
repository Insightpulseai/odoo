'use client'

import { client } from '@/lib/management-api'
import type { components } from '@/lib/management-api-schema'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type AxiosError } from 'axios'
import { toast } from 'sonner'

// GET Functions - List all functions
const getFunctions = async (projectRef: string) => {
  const { data, error } = await client.GET('/v1/projects/{ref}/functions', {
    params: {
      path: {
        ref: projectRef,
      },
    },
  })
  if (error) {
    throw error
  }

  return data
}

export const useGetFunctions = (projectRef: string) => {
  return useQuery({
    queryKey: ['functions', projectRef],
    queryFn: () => getFunctions(projectRef),
    enabled: !!projectRef,
    retry: false,
  })
}

// GET Function - Get a specific function by slug
const getFunction = async ({
  projectRef,
  functionSlug,
}: {
  projectRef: string
  functionSlug: string
}) => {
  const { data, error } = await client.GET('/v1/projects/{ref}/functions/{function_slug}', {
    params: {
      path: {
        ref: projectRef,
        function_slug: functionSlug,
      },
    },
  })
  if (error) {
    throw error
  }

  return data
}

export const useGetFunction = (projectRef: string, functionSlug: string) => {
  return useQuery({
    queryKey: ['functions', projectRef, functionSlug],
    queryFn: () => getFunction({ projectRef, functionSlug }),
    enabled: !!projectRef && !!functionSlug,
    retry: false,
  })
}

// DEPLOY Function - Use the correct /functions/deploy endpoint (NOT the deprecated /functions POST)
// This endpoint requires multipart/form-data with metadata and optional file(s)
type DeployFunctionParams = {
  projectRef: string
  slug: string
  metadata: components['schemas']['FunctionDeployBody']['metadata']
  files?: File[]
}

const deployFunction = async ({
  projectRef,
  slug,
  metadata,
  files,
}: DeployFunctionParams): Promise<components['schemas']['DeployFunctionResponse']> => {
  // Build multipart/form-data - this is REQUIRED for the /functions/deploy endpoint
  const formData = new FormData()

  // Metadata is required
  formData.append('metadata', JSON.stringify(metadata))

  // Files are optional but typically included for deployment
  if (files && files.length > 0) {
    files.forEach((file) => {
      formData.append('file', file)
    })
  }

  // Make a direct fetch call since openapi-fetch may not handle multipart properly
  const response = await fetch(
    `/api/supabase-proxy/v1/projects/${projectRef}/functions/deploy?slug=${encodeURIComponent(slug)}`,
    {
      method: 'POST',
      body: formData,
      // Do NOT set Content-Type header - browser will set it with correct boundary for multipart
    }
  )

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Deploy failed' }))
    throw new Error(errorData.message || `Deploy failed with status ${response.status}`)
  }

  return response.json()
}

export const useDeployFunction = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deployFunction,
    onSuccess: (data, variables) => {
      toast.success(`Function "${data.name || variables.slug}" deployed successfully.`)
      queryClient.invalidateQueries({
        queryKey: ['functions', variables.projectRef],
      })
    },
    onError: (error: Error | AxiosError<{ message: string }>) => {
      const message =
        'response' in error
          ? (error as AxiosError<{ message: string }>).response?.data?.message
          : error.message
      toast.error(message || 'Failed to deploy function.')
    },
  })
}

// DELETE Function
const deleteFunction = async ({
  projectRef,
  functionSlug,
}: {
  projectRef: string
  functionSlug: string
}) => {
  const { data, error } = await client.DELETE('/v1/projects/{ref}/functions/{function_slug}', {
    params: {
      path: {
        ref: projectRef,
        function_slug: functionSlug,
      },
    },
  })
  if (error) {
    throw error
  }

  return data
}

export const useDeleteFunction = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteFunction,
    onSuccess: (_, variables) => {
      toast.success(`Function "${variables.functionSlug}" deleted successfully.`)
      queryClient.invalidateQueries({
        queryKey: ['functions', variables.projectRef],
      })
    },
    onError: (error: AxiosError<{ message: string }>) => {
      toast.error(error.response?.data?.message || 'Failed to delete function.')
    },
  })
}
