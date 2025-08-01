export default function HowItWorks() {
  return (
    <section className="py-20">
      <div className="container-narrow">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            From Zero to AI Agent in 3 Simple Steps
          </h2>
          <p className="text-xl text-gray-600">
            No technical knowledge required. If you can copy and paste, you can deploy an AI agent.
          </p>
        </div>
        
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            {/* Connection line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300 hidden md:block"></div>
            
            <div className="space-y-12">
              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-xl font-bold relative z-10">
                  1
                </div>
                <div className="flex-grow">
                  <h3 className="text-2xl font-bold mb-2">Create Your Agent</h3>
                  <p className="text-gray-600 mb-4">
                    Sign up for free and create your AI agent. Give it a name, personality, 
                    and tell it about your business goals.
                  </p>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <code className="text-sm text-gray-700">
                      Agent Name: "Sarah - Sales Assistant"<br/>
                      Goal: Qualify B2B leads for SaaS product
                    </code>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-xl font-bold relative z-10">
                  2
                </div>
                <div className="flex-grow">
                  <h3 className="text-2xl font-bold mb-2">Train on Your Content</h3>
                  <p className="text-gray-600 mb-4">
                    Simply provide your website URL or upload documents. Our AI automatically 
                    learns everything about your business.
                  </p>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <code className="text-sm text-gray-700">
                      Website: https://yourcompany.com<br/>
                      Status: ✓ 47 pages indexed<br/>
                      Knowledge: Products, pricing, FAQs
                    </code>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center text-xl font-bold relative z-10">
                  3
                </div>
                <div className="flex-grow">
                  <h3 className="text-2xl font-bold mb-2">Copy & Deploy</h3>
                  <p className="text-gray-600 mb-4">
                    Copy our simple embed code and paste it into your website. Your AI agent 
                    is now live and ready to engage visitors.
                  </p>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <code className="text-sm text-gray-700">
                      &lt;script src="https://widget.netvexa.com/v1.js"&gt;&lt;/script&gt;<br/>
                      &lt;script&gt;netvexa.init('your-agent-id');&lt;/script&gt;
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}