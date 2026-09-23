import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "@/lib/api";
import { useCart } from "@/context/CartContext";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

export default function SharedBasket() {
  const { token } = useParams();
  const { add } = useCart();
  const nav = useNavigate();
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    api.get(`/baskets/${token}`)
      .then((r) => {
        const items = r.data.items || [];
        if (!items.length) { setStatus("empty"); return; }
        items.forEach((it) => {
          add({
            id: it.product_id, name: it.name, sku: it.sku,
            price_ex_vat: it.price_ex_vat, vat_rate: it.vat_rate,
            available_qty: it.available_qty, images: it.image ? [it.image] : [],
          }, it.quantity || 1);
        });
        toast.success("Shared basket added");
        nav("/cart");
      })
      .catch(() => setStatus("error"));
    // eslint-disable-next-line
  }, [token]);

  if (status === "loading") return <div className="gc-container py-20 text-center text-xl flex items-center justify-center gap-2"><Loader2 className="animate-spin" /> Loading shared basket…</div>;
  if (status === "empty") return <div className="gc-container py-20 text-center text-xl">This shared basket is empty.</div>;
  return <div className="gc-container py-20 text-center text-xl">This shared basket link is no longer available.</div>;
}
