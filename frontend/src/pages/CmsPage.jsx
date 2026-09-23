import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/lib/api";
import JsonLd from "@/components/JsonLd";

export default function CmsPage() {
  const { slug } = useParams();
  const [page, setPage] = useState(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    setPage(null); setErr(false);
    api.get(`/cms/page/${slug}`).then((r) => setPage(r.data)).catch(() => setErr(true));
  }, [slug]);

  if (err) return <div className="gc-container py-20 text-center text-xl">Page not found. <Link to="/" className="text-brand-terracotta underline">Go home</Link>.</div>;
  if (!page) return <div className="gc-container py-20 text-center text-xl">Loading…</div>;

  return (
    <div className="gc-container py-12 max-w-3xl" data-testid="cms-page">
      <JsonLd data={{ "@context": "https://schema.org", "@type": "WebPage", name: page.title, description: page.seo_description }} />
      <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-brand-green mb-8">{page.title}</h1>
      <div className="space-y-8">
        {(page.sections || []).map((s, i) => {
          if (s.type === "image" && s.url) return <img key={i} src={s.url} alt={s.alt || ""} className="w-full rounded-2xl" />;
          if (s.type === "html") return <div key={i} className="prose max-w-none" dangerouslySetInnerHTML={{ __html: s.body || "" }} />;
          return (
            <div key={i}>
              {s.heading && <h2 className="font-heading text-2xl font-bold text-brand-green mb-3">{s.heading}</h2>}
              {s.body && <p className="text-lg text-[#2D2D30] whitespace-pre-line">{s.body}</p>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
