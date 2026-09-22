import React from "react";

export function Privacy() {
  return (
    <div className="gc-container py-12 max-w-3xl">
      <h1 className="font-heading text-4xl font-extrabold text-brand-green mb-6">Privacy & cookies</h1>
      <div className="space-y-4 text-lg text-[#2D2D30]">
        <p>Grace Cares CIC is committed to protecting your personal data in line with UK GDPR. We only collect what we need to provide our services and process your orders, donations and enquiries.</p>
        <p><strong>Marketing consent</strong> is always optional, specific and unticked by default. Transactional emails (order, booking and donation confirmations) do not depend on marketing consent.</p>
        <p><strong>Sensitive information</strong>, including medical-condition details provided for VAT relief, is treated as sensitive personal information with additional protection and restricted access. We do not include medical information in ordinary notification emails.</p>
        <p>You can request a copy of your data or ask us to delete your account at any time from your account area, or by contacting us on 01543 730189.</p>
        <p className="text-base text-[#4A4A4D]">The final privacy notice, retention periods and lawful bases will be approved by Grace Cares before launch.</p>
      </div>
    </div>
  );
}

export function Terms() {
  return (
    <div className="gc-container py-12 max-w-3xl">
      <h1 className="font-heading text-4xl font-extrabold text-brand-green mb-6">Terms & conditions</h1>
      <div className="space-y-4 text-lg text-[#2D2D30]">
        <p>These terms govern the sale of pre-loved care equipment through Grace Cares. Most items are unique or available in limited quantities, and are sold as described.</p>
        <p>VAT relief is only applied where a product is approved as eligible <strong>and</strong> a valid customer declaration is completed. Being elderly on its own does not qualify, and a temporary condition does not normally qualify.</p>
        <p>Payments are processed securely by Stripe. We never store your full card details. Orders are only confirmed once payment is successfully received.</p>
        <p className="text-base text-[#4A4A4D]">Final terms and VAT wording will be approved by Grace Cares' accountant or VAT adviser before launch.</p>
      </div>
    </div>
  );
}

function PageShell({ title, intro, children }) {
  return (
    <div className="gc-container py-12 max-w-3xl">
      <h1 className="font-heading text-4xl font-extrabold text-brand-green mb-4">{title}</h1>
      {intro && <p className="text-xl text-[#4A4A4D] mb-8">{intro}</p>}
      <div className="space-y-4 text-lg text-[#2D2D30]">{children}</div>
    </div>
  );
}

const FAQS = [
  {
    q: "Is your equipment safe and clean?",
    a: "Yes. Every item is cleaned, inspected and — where relevant — PAT tested and safety-checked before it goes on sale. Each listing shows an honest condition grade and any cosmetic signs of previous use.",
  },
  {
    q: "How does VAT relief work?",
    a: "Some products qualify for VAT relief if you are disabled or have a long-term illness and the goods are for your personal or domestic use. Relief only applies where a product is approved as eligible and you complete a short declaration at checkout. Being elderly on its own, or a temporary condition, does not normally qualify.",
  },
  {
    q: "Can I collect, or do you deliver?",
    a: "Most items can be collected from our Lichfield hub. Smaller items can be posted, and we offer delivery on larger items — for bulky items we ask a few access questions and quote delivery separately after your order.",
  },
  {
    q: "Are items unique?",
    a: "Many of our items are one-offs. Once something sells it's gone, so if you've seen something you like we'd recommend not waiting too long. We add new stock every week.",
  },
  {
    q: "What if you don't have what I need?",
    a: "Tell us! Use the stock-alert form on the shop page or call us on 01543 730189 and we'll let you know as soon as something suitable comes in. We'll always try to help you find a solution.",
  },
  {
    q: "Can I donate equipment I no longer need?",
    a: "Absolutely — donating equipment keeps it out of landfill and helps another family. Visit our Donate Equipment page to tell us what you have and we'll arrange the next steps.",
  },
];

export function FAQs() {
  return (
    <PageShell title="Frequently asked questions" intro="Quick answers to the things people ask us most. Can't find what you need? Call 01543 730189.">
      <div className="space-y-3" data-testid="faq-list">
        {FAQS.map((f, i) => (
          <details key={i} className="group bg-white rounded-2xl border border-brand-border p-5" data-testid={`faq-${i}`}>
            <summary className="flex cursor-pointer items-center justify-between font-heading font-bold text-brand-green text-lg list-none">
              {f.q}
              <span className="ml-4 text-brand-terracotta text-2xl leading-none group-open:rotate-45 transition-transform">+</span>
            </summary>
            <p className="mt-3 text-[#2D2D30]">{f.a}</p>
          </details>
        ))}
      </div>
    </PageShell>
  );
}

export function Sustainability() {
  return (
    <PageShell title="Sustainability — our zero-to-landfill mission" intro="Every item reused is one less made, bought and thrown away. Here's how Grace Cares makes care sustainable.">
      <p>We rescue, refurbish and resell used care and mobility equipment so it can serve another family instead of ending up in landfill. It's better for people's pockets and better for the planet.</p>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">Reuse first</h2>
      <p>Where an item can be safely cleaned, repaired and re-tested, we give it a second life. Only when something genuinely can't be reused do we recycle its parts responsibly.</p>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">Measuring our impact</h2>
      <p>We estimate the carbon saved for each item reused, and show it on product pages so you can see the difference your purchase makes. Every penny of surplus is reinvested into free community programmes.</p>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">Supporting care providers' ESG goals</h2>
      <p>NHS trusts, care homes and businesses partner with us to divert equipment from waste and evidence their environmental and social commitments. Get in touch to find out more.</p>
    </PageShell>
  );
}

export function Returns() {
  return (
    <PageShell title="Returns & refunds" intro="We want you to be happy with your purchase. Here's what to expect if something isn't right.">
      <p>If an item arrives faulty or not as described, please contact us within 30 days on 01543 730189 or at hello@grace-cares.com and we'll put it right — a repair, replacement or refund as appropriate.</p>
      <p>As most of our equipment is pre-loved and often unique, items are sold as described with an honest condition grade. Please read the listing carefully and ask us anything before you buy.</p>
      <p>For hygiene and safety reasons, certain personal-use items cannot be returned once used unless they are faulty. This does not affect your statutory rights.</p>
      <p>Refunds are made to your original payment method. Where an item is collected or delivered, we'll agree the most practical way to return it with you.</p>
      <p className="text-base text-[#4A4A4D]">This summary will be finalised as part of our full terms before launch.</p>
    </PageShell>
  );
}

export function Accessibility() {
  return (
    <PageShell title="Accessibility statement" intro="We're committed to making grace-cares.com usable for everyone, whatever their ability or technology.">
      <p>We aim to meet the WCAG 2.2 AA standard. That means clear text at a comfortable size, strong colour contrast, keyboard-friendly navigation, and content that works with screen readers and when zoomed.</p>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">What we're doing</h2>
      <ul className="list-disc pl-6 space-y-2">
        <li>Readable base text and generous spacing throughout the site.</li>
        <li>Descriptive links, labels and image alternatives.</li>
        <li>A layout that reflows on small screens and at high zoom.</li>
        <li>Forms that clearly explain any errors.</li>
      </ul>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">Need help, or found a problem?</h2>
      <p>If you have trouble using any part of this site, or need information in a different format, please call 01543 730189 or email hello@grace-cares.com and we'll help right away.</p>
    </PageShell>
  );
}

export function CookiePolicy() {
  return (
    <PageShell title="Cookie policy" intro="How and why we use cookies on grace-cares.com.">
      <p>Cookies are small files stored on your device. We use a small number of them to make the site work and to understand how it's used.</p>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">Essential cookies</h2>
      <p>These keep you signed in, remember your basket and keep the site secure. The site cannot work properly without them.</p>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">Analytics cookies (optional)</h2>
      <p>With your consent, we use analytics to see which pages are popular so we can improve the site. These are never used for the medical-condition information provided for VAT relief.</p>
      <h2 className="font-heading text-2xl font-bold text-brand-green pt-4">Managing cookies</h2>
      <p>You can control or delete cookies in your browser settings at any time. Turning off essential cookies may stop parts of the site working.</p>
      <p className="text-base text-[#4A4A4D]">A full consent banner and cookie controls will be finalised before launch.</p>
    </PageShell>
  );
}
