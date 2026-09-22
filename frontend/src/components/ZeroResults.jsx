import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import { toast } from "sonner";

export default function ZeroResults({ q, cats = [] }) {
  const [fallback, setFallback] = useState([]);
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .get("/products?featured=true&in_stock=true&limit=3")
      .then((r) => setFallback(r.data.items || []))
      .catch(() => {});
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setBusy(true);
    try {
      await api.post("/stock-alerts", { email, query: q || "" });
      setSent(true);
      toast.success("We'll let you know when something matching arrives.");
    } catch {
      toast.error("Sorry, something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-8" data-testid="zero-results">
      <div className="bg-white rounded-2xl border border-brand-border p-8 text-center">
        <h2 className="font-heading text-2xl font-bold text-brand-green mb-2">
          {q ? <>No matches for “{q}”</> : "No products match those filters"}
        </h2>
        <p className="text-lg text-[#4A4A4D] mb-6">
          We add new stock every week. Browse a category below, or tell us what you need and we'll
          email you the moment it comes in.
        </p>

        {cats.length > 0 && (
          <div className="flex flex-wrap justify-center gap-3 mb-2">
            {cats.slice(0, 8).map((c) => (
              <a
                key={c.id}
                href={`/shop?category_id=${c.id}`}
                className="inline-flex items-center rounded-full border border-brand-green text-brand-green px-4 py-2 font-semibold hover:bg-brand-green hover:text-white transition-colors"
                data-testid={`zero-cat-${c.id}`}
              >
                {c.name}
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Stock alert */}
      <div className="bg-brand-green/5 rounded-2xl border border-brand-green/20 p-8">
        <h3 className="font-heading text-xl font-bold text-brand-green mb-2">Get a stock alert</h3>
        {sent ? (
          <p className="text-lg text-[#2f6b43] font-semibold" data-testid="stock-alert-done">
            Thanks — we've noted your interest{q ? <> in “{q}”</> : null} and will be in touch.
          </p>
        ) : (
          <form onSubmit={submit} className="flex flex-col sm:flex-row gap-3 max-w-xl" data-testid="stock-alert-form">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Your email address"
              aria-label="Your email address"
              className="flex-1 rounded-full border border-[#8C8C8C] px-4 py-3"
              data-testid="stock-alert-email"
            />
            <button
              type="submit"
              disabled={busy}
              className="rounded-full bg-brand-green text-white px-6 py-3 font-semibold disabled:opacity-60"
              data-testid="stock-alert-submit"
            >
              {busy ? "Sending…" : "Notify me"}
            </button>
          </form>
        )}
      </div>

      {fallback.length > 0 && (
        <div>
          <h3 className="font-heading text-xl font-bold text-brand-green mb-4">You might also like</h3>
          <div className="grid gap-8 sm:grid-cols-2 xl:grid-cols-3">
            {fallback.map((p) => (
              <ProductCard key={p.id} p={p} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
