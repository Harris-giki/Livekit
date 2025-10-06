import { headers } from "next/headers";
import { getAppConfig } from "@/lib/utils";

interface AppLayoutProps {
  children: React.ReactNode;
}

export default async function AppLayout({ children }: AppLayoutProps) {
  const hdrs = await headers();
  await getAppConfig(hdrs);

  return (
    <>
      <header className="fixed top-0 left-0 z-50 hidden w-full flex-row justify-between p-6 md:flex">
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://www.linkedin.com/in/harris-giki"
          className="scale-100 transition-transform duration-300 hover:scale-110"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/radiance.png"
            alt="Radiance Logo"
            width={120}
            height={40}
          />
        </a>
      </header>
      {children}
    </>
  );
}
