import { NextRequest, NextResponse } from 'next/server'
import { cms } from '@/lib/supabase-cms'

/**
 * CMS API Route
 * Example: GET /api/cms?category=news&page=1&perPage=10
 */
export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const category = searchParams.get('category') || undefined
  const tag = searchParams.get('tag') || undefined
  const search = searchParams.get('search') || undefined
  const page = searchParams.get('page')
    ? parseInt(searchParams.get('page')!)
    : undefined
  const perPage = searchParams.get('perPage')
    ? parseInt(searchParams.get('perPage')!)
    : undefined

  try {
    const response = await cms.getPosts({
      category,
      tag,
      search,
      page,
      perPage,
    })

    if (response.error) {
      return NextResponse.json(
        { error: response.error },
        { status: 500 }
      )
    }

    return NextResponse.json(response)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch posts' },
      { status: 500 }
    )
  }
}

/**
 * Create a new post
 * POST /api/cms
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const response = await cms.createPost(body)

    if (response.error) {
      return NextResponse.json(
        { error: response.error },
        { status: 500 }
      )
    }

    return NextResponse.json(response, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create post' },
      { status: 500 }
    )
  }
}
