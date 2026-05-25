import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Connor Burdick | Goalkeeper Soccer Recruit | Class of 2028",
  description:
    "NCAA goalkeeper recruiting profile for Connor Burdick, Class of 2028, training in Madrid with strong academics and technical building experience.",
  openGraph: {
    title: "Connor Burdick | Goalkeeper Soccer Recruit | Class of 2028",
    description:
      "International goalkeeper recruit training in Madrid with a strong academic trajectory and technical builder profile.",
    type: "profile",
  },
  twitter: {
    card: "summary_large_image",
    title: "Connor Burdick | Goalkeeper Soccer Recruit | Class of 2028",
    description:
      "International goalkeeper recruit training in Madrid with a strong academic trajectory and technical builder profile.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased scroll-smooth">
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100">
        {children}
      </body>
    </html>
  );
}
