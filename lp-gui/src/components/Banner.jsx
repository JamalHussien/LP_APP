import React from "react";

function Banner({ tone = "info", children }) {
  const toneClass =
    tone === "error"
      ? "banner-error"
      : tone === "success"
      ? "banner-success"
      : "results-surface";
  return <div className={toneClass}>{children}</div>;
}

export default Banner;
