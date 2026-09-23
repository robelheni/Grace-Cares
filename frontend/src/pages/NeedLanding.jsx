import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import JsonLd from "@/components/JsonLd";

export default function NeedLanding() {
  const { slug } = useParams();
  const [page, setPage] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    setPage(null); setErr(false);
    api.get(`/landing/${slug}`).then((r) => setPage(r.data)).catch(() => setErr(true));
  }, [slug]);

  if (err) return <div className="gc-container py-20 text-center text-xl">Page not found. <Link to="/shop" className="text-brand-terracotta underline">Browse the shop</Link>.</div>;
  if (!page) return <div className="gc-container py-20 text-center text-xl">Loading…</div>;

  return (
    <div className="gc-container py-12" data-testid="need-landing">
      <JsonLd data={{ "@context": "https://schema.org", "@type": "WebPage", name: page.title, description: page.intro }} />
      <div className="max-w-3xl">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-brand-green mb-4">{page.title}</h1>
        <p className="text-xl text-[#4A4A4D] mb-6">{page.intro}</p>
        {page.body && <p className="text-lg text-[#2D2D30] mb-8">{page.body}</p>}
      </div>

      {(page.products || []).length > 0 && (
        <>
          <h2 className="font-heading text-2xl font-bold text-brand-green mb-4">Equipment that can help</h2>
          <div className="grid gap-8 sm:grid-cols-2 xl:grid-cols-3 mb-12">
            {page.products.map((p) => <ProductCard key={p.id} p={p} />)}
          </div>
        </>
      )}

      {(page.faqs || []).length > 0 && (
        <div className="max-w-3xl space-y-3">
          <h2 className="font-heading text-2xl font-bold text-brand-green mb-2">Common questions</h2>
          {page.faqs.map((f, i) => (
            <details key={i} className="bg-white rounded-2xl border border-brand-border p-5">
              <summary className="cursor-pointer font-heading font-bold text-brand-green">{f.q}</summary>
              <p className="mt-2 text-[#2D2D30]">{f.a}</p>
            </details>
          ))}
        </div>
      )}

      <div className="mt-10 bg-brand-green/5 rounded-2xl p-6 text-center">
        <p className="text-lg mb-3">Not sure what you need? We're happy to help — no pressure.</p>
        <a href="tel:01543730189" className="inline-block bg-brand-green text-white rounded-full px-6 py-3 font-semibold">Call 01543 730189</a>
      </div>
    </div>
  );
}
