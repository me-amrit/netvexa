import { GetStaticProps } from 'next'
import { NextSeo } from 'next-seo'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import { getSortedPostsData, PostData } from '@/lib/blog'

interface BlogProps {
  allPostsData: PostData[]
}

export default function Blog({ allPostsData }: BlogProps) {
  return (
    <>
      <NextSeo
        title="Blog - AI Business Automation Insights"
        description="Learn how to leverage AI agents for lead generation, customer support, and business growth. Expert insights for SMEs and enterprise."
        canonical="https://netvexa.com/blog"
      />
      
      <div className="min-h-screen bg-white">
        <Navbar />
        
        <section className="pt-32 pb-20">
          <div className="container-narrow">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
                Insights & Resources
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Learn how leading businesses use AI agents to transform customer engagement, 
                automate lead qualification, and scale revenue.
              </p>
            </div>
            
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {allPostsData.map((post) => (
                <article key={post.slug} className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow">
                  {post.image && (
                    <div className="aspect-w-16 aspect-h-9 bg-gray-100">
                      <img 
                        src={post.image} 
                        alt={post.title}
                        className="object-cover w-full h-48"
                      />
                    </div>
                  )}
                  <div className="p-6">
                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                      <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                        {post.category}
                      </span>
                      <span>{post.readTime}</span>
                    </div>
                    <h2 className="text-xl font-bold mb-2 line-clamp-2">
                      <Link href={`/blog/${post.slug}`} className="hover:text-primary transition-colors">
                        {post.title}
                      </Link>
                    </h2>
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {post.excerpt}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-500">
                        <span>{post.author}</span> • <span>{new Date(post.date).toLocaleDateString()}</span>
                      </div>
                      <Link 
                        href={`/blog/${post.slug}`}
                        className="text-primary font-semibold hover:underline"
                      >
                        Read more →
                      </Link>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
        
        <Footer />
      </div>
    </>
  )
}

export const getStaticProps: GetStaticProps = async () => {
  const allPostsData = getSortedPostsData()
  return {
    props: {
      allPostsData,
    },
  }
}