import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Star } from "lucide-react";
import { toast } from "sonner";

function Stars({ value, onChange }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type={onChange ? "button" : undefined}
          onClick={onChange ? () => onChange(n) : undefined}
          className={onChange ? "cursor-pointer" : "cursor-default"}
          aria-label={`${n} star${n > 1 ? "s" : ""}`}
        >
          <Star size={20} className={n <= value ? "fill-brand-terracotta text-brand-terracotta" : "text-brand-border"} />
        </button>
      ))}
    </div>
  );
}

export default function Reviews({ productId }) {
  const [data, setData] = useState({ items: [], aggregate: { average: 0, count: 0 } });
  const [show, setShow] = useState(false);
  const [form, setForm] = useState({ order_reference: "", email: "", author_name: "", rating: 5, title: "", body: "" });
  const [busy, setBusy] = useState(false);

  const load = () => api.get(`/products/${productId}/reviews`).then((r) => setData(r.data)).catch(() => {});
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [productId]);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const r = await api.post("/reviews", { product_id: productId, ...form });
      toast.success(r.data.message || "Thank you for your review!");
      setShow(false);
      setForm({ order_reference: "", email: "", author_name: "", rating: 5, title: "", body: "" });
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Could not submit review.");
    } finally {
      setBusy(false);
    }
  };

  const agg = data.aggregate || { average: 0, count: 0 };

  return (
    <div className="mt-10" data-testid="reviews-section">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
        <h2 className="font-heading text-2xl font-bold text-brand-green">Customer reviews</h2>
        <button onClick={() => setShow(!show)} className="rounded-full border-2 border-brand-green text-brand-green px-5 py-2 font-semibold hover:bg-brand-green hover:text-white transition-colors" data-testid="write-review-btn">
          Write a review
        </button>
      </div>

      {agg.count > 0 ? (
        <div className="flex items-center gap-3 mb-6" data-testid="review-aggregate">
          <Stars value={Math.round(agg.average)} />
          <span className="font-bold text-lg">{agg.average}</span>
          <span className="text-[#4A4A4D]">based on {agg.count} review{agg.count > 1 ? "s" : ""}</span>
        </div>
      ) : (
        <p className="text-[#4A4A4D] mb-6">No reviews yet. Bought this item? Be the first to review it.</p>
      )}

      {show && (
        <form onSubmit={submit} className="bg-white rounded-2xl border border-brand-border p-6 mb-6 space-y-3" data-testid="review-form">
          <p className="text-sm text-[#4A4A4D]">Reviews are tied to a real order. Enter your order reference and the email you used.</p>
          <div className="grid sm:grid-cols-2 gap-3">
            <input required placeholder="Order reference (e.g. GC-12345678)" value={form.order_reference} onChange={(e) => setForm({ ...form, order_reference: e.target.value })} className="rounded-lg border border-[#8C8C8C] px-3 py-2.5" data-testid="review-order-ref" />
            <input required type="email" placeholder="Your email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="rounded-lg border border-[#8C8C8C] px-3 py-2.5" data-testid="review-email" />
          </div>
          <input required placeholder="Your name (shown publicly)" value={form.author_name} onChange={(e) => setForm({ ...form, author_name: e.target.value })} className="w-full rounded-lg border border-[#8C8C8C] px-3 py-2.5" data-testid="review-name" />
          <div className="flex items-center gap-3"><span className="font-semibold">Rating:</span><Stars value={form.rating} onChange={(n) => setForm({ ...form, rating: n })} /></div>
          <input placeholder="Title (optional)" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full rounded-lg border border-[#8C8C8C] px-3 py-2.5" data-testid="review-title" />
          <textarea required placeholder="Tell others about your experience" value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} rows={4} className="w-full rounded-lg border border-[#8C8C8C] px-3 py-2.5" data-testid="review-body" />
          <button disabled={busy} className="rounded-full bg-brand-green text-white px-6 py-2.5 font-semibold disabled:opacity-60" data-testid="review-submit">{busy ? "Submitting…" : "Submit review"}</button>
        </form>
      )}

      <div className="space-y-4">
        {(data.items || []).map((r) => (
          <div key={r.id} className="bg-white rounded-2xl border border-brand-border p-5" data-testid="review-item">
            <div className="flex items-center gap-3 mb-1">
              <Stars value={r.rating} />
              {r.verified && <span className="text-xs font-bold text-[#1B5E20] bg-[#E8F5E9] px-2 py-0.5 rounded-full">Verified purchase</span>}
            </div>
            {r.title && <div className="font-heading font-bold text-brand-green">{r.title}</div>}
            <p className="text-[#2D2D30]">{r.body}</p>
            <div className="text-sm text-[#8C8C8C] mt-1">{r.author_name}</div>
            {r.response && <div className="mt-2 bg-brand-green/5 rounded-lg p-3 text-sm"><strong>Grace Cares:</strong> {r.response}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
