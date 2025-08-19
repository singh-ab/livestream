import "./globals.css";
import React from "react";

export const metadata = {
  title: "Livestream App",
  description: "RTSP livestream viewer with overlays",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
