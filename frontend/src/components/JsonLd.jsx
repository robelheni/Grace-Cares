import React from "react";

// Renders JSON-LD structured data. In an SPA this lands in the DOM where
// crawlers that execute JS (Google) can read it.
export default function JsonLd({ data }) {
  if (!data) return null;
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
