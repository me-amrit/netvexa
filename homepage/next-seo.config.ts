import { DefaultSeoProps } from 'next-seo';

const config: DefaultSeoProps = {
  titleTemplate: '%s | NETVEXA - AI Business Agent',
  defaultTitle: 'NETVEXA - Deploy AI Business Agents in 60 Minutes',
  description: 'Transform your website into a 24/7 sales machine. NETVEXA\'s AI agents qualify leads, answer questions, and convert visitors while you sleep. GDPR compliant, no coding required.',
  canonical: 'https://netvexa.com',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://netvexa.com',
    siteName: 'NETVEXA',
    title: 'NETVEXA - AI Business Agent Platform',
    description: 'Deploy intelligent AI agents on your website in under 60 minutes. Qualify leads, answer questions, and grow revenue 24/7.',
    images: [
      {
        url: 'https://netvexa.com/og-image.png',
        width: 1200,
        height: 630,
        alt: 'NETVEXA AI Business Agent',
      },
    ],
  },
  twitter: {
    handle: '@netvexa',
    site: '@netvexa',
    cardType: 'summary_large_image',
  },
  additionalMetaTags: [
    {
      name: 'viewport',
      content: 'width=device-width, initial-scale=1',
    },
    {
      name: 'keywords',
      content: 'AI chatbot, business automation, lead generation, customer support, WordPress plugin, Shopify app, GDPR compliant, RAG technology',
    },
  ],
  additionalLinkTags: [
    {
      rel: 'icon',
      href: '/favicon.ico',
    },
  ],
};

export default config;