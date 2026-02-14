import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers':
    'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    )

    const url = new URL(req.url)
    const pathParts = url.pathname.split('/').filter(Boolean)
    const slug = pathParts[pathParts.length - 1]

    // GET /posts-api or /posts-api/:slug
    if (req.method === 'GET') {
      // Get single post by slug
      if (slug && slug !== 'posts-api') {
        const { data: post, error } = await supabaseClient
          .from('cms_posts')
          .select(
            `
            *,
            categories:cms_post_categories(category:cms_categories(*)),
            tags:cms_post_tags(tag:cms_tags(*))
          `
          )
          .eq('slug', slug)
          .eq('status', 'published')
          .single()

        if (error) {
          return new Response(JSON.stringify({ error: error.message }), {
            status: 404,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          })
        }

        // Flatten categories and tags
        const formattedPost = {
          ...post,
          categories: post.categories?.map((c: any) => c.category.name) || [],
          tags: post.tags?.map((t: any) => t.tag.name) || [],
        }

        return new Response(JSON.stringify({ data: formattedPost }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      // Get all posts with filters
      const category = url.searchParams.get('category')
      const tag = url.searchParams.get('tag')
      const search = url.searchParams.get('search')
      const page = parseInt(url.searchParams.get('page') || '1')
      const perPage = parseInt(url.searchParams.get('perPage') || '10')

      let query = supabaseClient
        .from('cms_posts')
        .select(
          `
          *,
          categories:cms_post_categories(category:cms_categories(*)),
          tags:cms_post_tags(tag:cms_tags(*))
        `,
          { count: 'exact' }
        )
        .eq('status', 'published')
        .order('published_at', { ascending: false })

      // Apply filters
      if (search) {
        query = query.or(
          `title.ilike.%${search}%,content.ilike.%${search}%,excerpt.ilike.%${search}%`
        )
      }

      // Pagination
      const from = (page - 1) * perPage
      const to = from + perPage - 1
      query = query.range(from, to)

      const { data: posts, error, count } = await query

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      // Format posts
      const formattedPosts = posts?.map((post: any) => ({
        ...post,
        categories: post.categories?.map((c: any) => c.category.name) || [],
        tags: post.tags?.map((t: any) => t.tag.name) || [],
      }))

      // Filter by category/tag if needed (post-query filtering)
      let filteredPosts = formattedPosts
      if (category) {
        filteredPosts = filteredPosts?.filter((p: any) =>
          p.categories.includes(category)
        )
      }
      if (tag) {
        filteredPosts = filteredPosts?.filter((p: any) => p.tags.includes(tag))
      }

      return new Response(
        JSON.stringify({
          data: filteredPosts,
          pagination: {
            page,
            perPage,
            total: count || 0,
          },
        }),
        {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        }
      )
    }

    // POST /posts-api - Create new post
    if (req.method === 'POST') {
      const body = await req.json()

      const { data: post, error } = await supabaseClient
        .from('cms_posts')
        .insert({
          title: body.title,
          slug: body.slug,
          content: body.content,
          excerpt: body.excerpt,
          author: body.author,
          published_at: body.publishedAt || new Date().toISOString(),
          seo_title: body.seoTitle,
          seo_description: body.seoDescription,
          featured_image: body.featuredImage,
          status: body.status || 'draft',
        })
        .select()
        .single()

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      return new Response(JSON.stringify({ data: post }), {
        status: 201,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // PUT /posts-api/:id - Update post
    if (req.method === 'PUT') {
      const id = slug
      const body = await req.json()

      const { data: post, error } = await supabaseClient
        .from('cms_posts')
        .update({
          title: body.title,
          slug: body.slug,
          content: body.content,
          excerpt: body.excerpt,
          author: body.author,
          published_at: body.publishedAt,
          seo_title: body.seoTitle,
          seo_description: body.seoDescription,
          featured_image: body.featuredImage,
          status: body.status,
        })
        .eq('id', id)
        .select()
        .single()

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      return new Response(JSON.stringify({ data: post }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    // DELETE /posts-api/:id - Delete post
    if (req.method === 'DELETE') {
      const id = slug

      const { error } = await supabaseClient
        .from('cms_posts')
        .delete()
        .eq('id', id)

      if (error) {
        return new Response(JSON.stringify({ error: error.message }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        })
      }

      return new Response(JSON.stringify({ data: null }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      })
    }

    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    })
  }
})
