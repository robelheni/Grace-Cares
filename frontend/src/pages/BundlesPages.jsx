import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { api, gbp } from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import { useCart } from "@/context/CartContext";
import { Package, ArrowRight } from "lucide-react";
import { toast } from "sonner";

export function Bundles() {
  const [bundles, setBundles] = useState([]);
  useEffect(() => { api.get("/bundles").then((r) => setBundles(r.data)).catch(() => {}); }, []);
  return (
    <div className="gc-container py-12" data-testid="bundles-page">
      <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-brand-green mb-3">Ready-made bundles</h1>
      <p className="text-xl text-[#4A4A4D] mb-8 max-w-2xl">Carefully chosen sets of equipment for common situations — add everything to your basket in one click.</p>
      <div className="grid gap-8 md:grid-cols-3">
        {bundles.map((b) => (
          <Link key={b.slug} to={`/bundles/${b.slug}`} className="bg-white rounded-2xl border border-brand-border p-6 hover:shadow-md transition-shadow flex flex-col" data-testid={`bundle-${b.slug}`}>
            <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-brand-green/10 text-brand-green mb-4"><Package size={24} /></div>
            <h2 className="font-heading text-xl font-bold text-brand-green mb-2">{b.title}</h2>
            <p className="text-[#4A4A4D] flex-grow">{b.description}</p>
            <div className="mt-4 flex items-center justify-between">
              <span className="font-bold text-lg">{b.item_count} items · {gbp(b.total)}</span>
              <ArrowRight className="text-brand-terracotta" />
            </div>
            {b.saving > 0 && <span className="mt-2 inline-block text-sm font-bold text-brand-terracotta">Save {gbp(b.saving)} vs new</span>}
          </Link>
        ))}
      </div>
    </div>
  );
}

export function BundleDetail() {
  const { slug } = useParams();
  const [bundle, setBundle] = useState(null);
  const [err, setErr] = useState(false);
  const { add } = useCart();
  const nav = useNavigate();

  useEffect(() => {
    setBundle(null); setErr(false);
    api.get(`/bundles/${slug}`).then((r) => setBundle(r.data)).catch(() => setErr(true));
  }, [slug]);

  if (err) return <div className="gc-container py-20 text-center text-xl">Bundle not found. <Link to="/bundles" className="text-brand-terracotta underline">See all bundles</Link>.</div>;
  if (!bundle) return <div className="gc-container py-20 text-center text-xl">Loading…</div>;

  const addAll = () => {
    let added = 0;
    (bundle.products || []).forEach((p) => { if ((p.available_qty ?? 0) > 0) { add(p, 1); added++; } });
    if (added) { toast.success("Bundle added to your basket"); nav("/cart"); }
    else toast.error("These items are currently unavailable.");
  };

  return (
    <div className="gc-container py-12" data-testid="bundle-detail">
      <Link to="/bundles" className="text-brand-terracotta underline">← All bundles</Link>
      <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-brand-green mt-3 mb-3">{bundle.title}</h1>
      <p className="text-xl text-[#4A4A4D] mb-6 max-w-2xl">{bundle.description}</p>

      <div className="bg-white rounded-2xl border border-brand-border p-6 mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="text-2xl font-bold text-brand-green">{gbp(bundle.total)}</div>
          {bundle.saving > 0 && <div className="text-brand-terracotta font-semibold">Save {gbp(bundle.saving)} vs buying new</div>}
        </div>
        <button onClick={addAll} className="bg-brand-terracotta text-white rounded-full px-7 py-3.5 font-semibold text-lg hover:bg-brand-terracottahover transition-colors" data-testid="add-bundle-btn">Add bundle to basket</button>
      </div>

      <div className="grid gap-8 sm:grid-cols-2 xl:grid-cols-3">
        {(bundle.products || []).map((p) => <ProductCard key={p.id} p={p} />)}
      </div>
    </div>
  );
}
