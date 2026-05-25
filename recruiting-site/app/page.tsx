import FadeIn from "@/components/FadeIn";

export default function Home() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Athlete",
    name: "Connor Burdick",
    description:
      "Goalkeeper recruit, Class of 2028, training in Madrid with strong academic growth and technical builder profile.",
    height: "6'2\"",
    weight: "165 lbs",
    sport: "Soccer",
    nationality: "American",
    alumniOf: "Brewster Madrid (American School)",
    sameAs: [
      "https://github.com/cburdick28-spec",
      "https://www.instagram.com/burdickconnor/",
    ],
    email: "connorburdick@gmail.com",
    homeLocation: {
      "@type": "Place",
      name: "Madrid, Spain",
    },
  };

  return (
    <>
      <main className="flex-1">
        <section
          id="hero"
          className="relative min-h-screen overflow-hidden border-b border-white/10"
        >
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.25),_transparent_55%),radial-gradient(circle_at_20%_20%,_rgba(14,116,144,0.25),_transparent_45%),linear-gradient(135deg,_rgba(15,23,42,1)_0%,_rgba(2,6,23,1)_50%,_rgba(15,23,42,1)_100%)]" />
          <div className="absolute inset-0 opacity-30 mix-blend-screen bg-[radial-gradient(circle_at_80%_20%,_rgba(255,255,255,0.2),_transparent_40%)]" />
          <div className="relative mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-center px-6 py-20">
            <FadeIn className="max-w-3xl">
              <p className="text-sm uppercase tracking-[0.3em] text-slate-400">
                NCAA Recruiting Profile
              </p>
              <h1 className="mt-4 text-5xl font-semibold tracking-tight text-white sm:text-6xl">
                Connor Burdick
              </h1>
              <p className="mt-4 text-lg text-slate-200 sm:text-xl">
                Goalkeeper | Class of 2028 | Madrid, Spain
              </p>
              <p className="mt-6 text-lg leading-relaxed text-slate-300">
                International student-athlete combining elite soccer development
                with strong academics and technical building skills.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <a
                  href="#showcase"
                  className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
                >
                  Watch Footage
                </a>
                <a
                  href="#snapshot"
                  className="rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/50 hover:bg-white/5"
                >
                  Recruiting Profile
                </a>
              </div>
            </FadeIn>
            <FadeIn className="mt-12 grid gap-3 text-sm text-slate-200 sm:grid-cols-3 lg:grid-cols-6">
              {[
                "6’2”",
                "165 lbs",
                "Right Foot",
                "GPA 3.6",
                "Brewster Madrid",
                "USA",
              ].map((stat) => (
                <div
                  key={stat}
                  className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-center backdrop-blur"
                >
                  {stat}
                </div>
              ))}
            </FadeIn>
          </div>
        </section>

        <section id="snapshot" className="py-20">
          <div className="mx-auto w-full max-w-6xl px-6">
            <FadeIn>
              <h2 className="text-3xl font-semibold text-white">
                Quick Player Snapshot
              </h2>
              <p className="mt-3 text-slate-300">
                Coach-first summary focused on immediate evaluation in 5–10
                seconds.
              </p>
            </FadeIn>
            <div className="mt-10 grid gap-6 md:grid-cols-2">
              {[
                {
                  title: "Position",
                  text: "Primary goalkeeper with forward/striker experience for added attacking insight.",
                },
                {
                  title: "Play Style",
                  text: "Modern goalkeeper with confident distribution, proactive starting positions, and calm decision-making.",
                },
                {
                  title: "Academics",
                  text: "3.6 GPA with clear upward trajectory and STEM focus.",
                },
                {
                  title: "Builder",
                  text: "AI + software engineering projects demonstrating discipline, creativity, and systems thinking.",
                },
              ].map((item) => (
                <FadeIn
                  key={item.title}
                  className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur"
                >
                  <h3 className="text-xl font-semibold text-white">
                    {item.title}
                  </h3>
                  <p className="mt-3 text-slate-300">{item.text}</p>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        <section id="showcase" className="border-t border-white/10 py-20">
          <div className="mx-auto w-full max-w-6xl px-6">
            <FadeIn>
              <h2 className="text-3xl font-semibold text-white">
                Showcase Evaluation Footage
              </h2>
              <p className="mt-3 text-slate-300">
                Live competitive showcase footage highlighting goalkeeper shot
                stopping, positioning, distribution, aerial control, and
                decision-making under pressure.
              </p>
            </FadeIn>
            <FadeIn className="mt-10 overflow-hidden rounded-2xl border border-white/10 bg-black/40 shadow-[0_30px_80px_rgba(0,0,0,0.4)]">
              <div className="aspect-video w-full">
                <iframe
                  className="h-full w-full"
                  src="https://www.youtube.com/embed/N_aLIddx_Cs"
                  title="Showcase Evaluation Footage"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            </FadeIn>
            <FadeIn className="mt-6">
              <p className="text-slate-300">
                Additional full match footage available in the Film Library.
              </p>
              <a
                href="https://drive.google.com/drive/folders/1US8sQDyp60TCfVF0GXDffc9hryI3uLw6?usp=drive_link"
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-sky-300 transition hover:text-sky-200"
              >
                View Full Film Library →
              </a>
            </FadeIn>
          </div>
        </section>

        <section id="library" className="border-t border-white/10 py-20">
          <div className="mx-auto w-full max-w-6xl px-6">
            <FadeIn>
              <h2 className="text-3xl font-semibold text-white">
                Complete Goalkeeper Film Library
              </h2>
              <p className="mt-3 text-slate-300">
                Organized, recruiter-first access to every relevant evaluation
                sequence.
              </p>
            </FadeIn>
            <div className="mt-10 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
              <FadeIn className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <h3 className="text-xl font-semibold text-white">
                  Film Library Contents
                </h3>
                <ul className="mt-4 grid gap-2 text-slate-300">
                  {[
                    "Shot stopping clips",
                    "1v1 situations",
                    "Crosses and aerial claims",
                    "Distribution and build-out play",
                    "Full match footage",
                    "Training and technical work",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <span className="mt-1 h-2 w-2 rounded-full bg-sky-400" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </FadeIn>
              <FadeIn className="flex flex-col justify-between rounded-2xl border border-white/10 bg-slate-900/70 p-6">
                <div>
                  <h3 className="text-xl font-semibold text-white">
                    Recruiter Access
                  </h3>
                  <p className="mt-3 text-slate-300">
                    All clips and matches are hosted in a dedicated Google Drive
                    hub for easy review.
                  </p>
                </div>
                <a
                  href="https://drive.google.com/drive/folders/1US8sQDyp60TCfVF0GXDffc9hryI3uLw6?usp=drive_link"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-6 inline-flex items-center justify-center rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
                >
                  Open Film Library
                </a>
              </FadeIn>
            </div>
          </div>
        </section>

        <section id="scouting" className="border-t border-white/10 py-20">
          <div className="mx-auto w-full max-w-6xl px-6">
            <FadeIn>
              <h2 className="text-3xl font-semibold text-white">
                Goalkeeper Scouting Report
              </h2>
              <p className="mt-3 text-slate-300">
                Evaluated through live match performance and showcase play.
              </p>
            </FadeIn>
            <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  title: "Shot Stopping",
                  text: "Quick reactions with confident handling and controlled parries in traffic.",
                },
                {
                  title: "1v1 Ability",
                  text: "Composed in breakaways, closing angles early while staying balanced.",
                },
                {
                  title: "Distribution",
                  text: "Comfortable initiating attacks with accurate throws and clipped passes.",
                },
                {
                  title: "Positioning",
                  text: "Reads the game early, staying connected to back line and space behind.",
                },
                {
                  title: "Aerial Control",
                  text: "Aggressive on crosses with clean timing and secure claims.",
                },
                {
                  title: "Communication",
                  text: "Organizes defenders with clear direction in transition moments.",
                },
                {
                  title: "Tactical Awareness",
                  text: "Striker experience adds attacking movement awareness and transition intelligence.",
                },
              ].map((item) => (
                <FadeIn
                  key={item.title}
                  className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur"
                >
                  <h3 className="text-xl font-semibold text-white">
                    {item.title}
                  </h3>
                  <p className="mt-3 text-slate-300">{item.text}</p>
                </FadeIn>
              ))}
            </div>
          </div>
        </section>

        <section id="international" className="border-t border-white/10 py-20">
          <div className="mx-auto w-full max-w-6xl px-6">
            <FadeIn className="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900/80 via-slate-950 to-slate-900/80 p-8">
              <h2 className="text-3xl font-semibold text-white">
                International Development | Madrid, Spain
              </h2>
              <p className="mt-4 text-slate-300">
                Training and competing in Madrid provides daily exposure to
                diverse playing styles, faster tempo, and tactical demands that
                sharpen decision-making under pressure.
              </p>
              <div className="mt-6 grid gap-4 md:grid-cols-3">
                {[
                  "Adapted to multiple tactical systems and coaching methods.",
                  "Comfortable communicating across cultures and environments.",
                  "Consistent growth through high-level training standards.",
                ].map((item) => (
                  <div
                    key={item}
                    className="rounded-xl border border-white/10 bg-white/5 p-4 text-sm text-slate-200"
                  >
                    {item}
                  </div>
                ))}
              </div>
            </FadeIn>
          </div>
        </section>

        <section id="academics" className="border-t border-white/10 py-20">
          <div className="mx-auto w-full max-w-6xl px-6">
            <FadeIn>
              <h2 className="text-3xl font-semibold text-white">
                Academics + Builder Profile
              </h2>
              <p className="mt-3 text-slate-300">
                Built Beyond Soccer — elite athlete, technical creator, systems
                thinker.
              </p>
            </FadeIn>
            <div className="mt-10 grid gap-6 lg:grid-cols-2">
              <FadeIn className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <h3 className="text-xl font-semibold text-white">Academics</h3>
                <ul className="mt-4 grid gap-2 text-slate-300">
                  {[
                    "GPA progression: 2.6 → 3.6",
                    "Strong STEM performance with upward trajectory",
                    "Business + Computer Science strengths",
                    "Disciplined improvement arc and coachability",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <span className="mt-1 h-2 w-2 rounded-full bg-sky-400" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </FadeIn>
              <FadeIn className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <h3 className="text-xl font-semibold text-white">
                  Builder Portfolio
                </h3>
                <p className="mt-3 text-slate-300">
                  AI tools, apps, simulations, and systems-focused builds that
                  reflect analytical thinking and initiative.
                </p>
                <div className="mt-4 flex flex-wrap gap-3 text-sm text-slate-200">
                  {[
                    "BrewsterApp",
                    "BrewsterAI",
                    "Soccersim",
                    "futtysim",
                    "AI tools",
                    "Simulations",
                  ].map((item) => (
                    <span
                      key={item}
                      className="rounded-full border border-white/10 bg-slate-900/80 px-4 py-2"
                    >
                      {item}
                    </span>
                  ))}
                </div>
                <a
                  href="https://github.com/cburdick28-spec"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-sky-300 transition hover:text-sky-200"
                >
                  View GitHub →
                </a>
              </FadeIn>
            </div>
          </div>
        </section>

        <section id="contact" className="border-t border-white/10 py-20">
          <div className="mx-auto w-full max-w-6xl px-6">
            <FadeIn className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur">
              <p className="text-sm uppercase tracking-[0.3em] text-slate-400">
                Open to Recruiting Opportunities
              </p>
              <h2 className="mt-4 text-3xl font-semibold text-white">
                GK | Class of 2028 | 6’2” | 165 lbs | Madrid, Spain | GPA 3.6
              </h2>
              <div className="mt-6 flex flex-col items-center gap-2 text-slate-300">
                <a
                  href="mailto:connorburdick@gmail.com"
                  className="text-lg font-semibold text-white"
                >
                  connorburdick@gmail.com
                </a>
                <a
                  href="https://www.instagram.com/burdickconnor/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-sky-300 transition hover:text-sky-200"
                >
                  Instagram: @burdickconnor
                </a>
              </div>
              <div className="mt-8 flex flex-wrap justify-center gap-4">
                <a
                  href="mailto:connorburdick@gmail.com"
                  className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
                >
                  Contact
                </a>
                <a
                  href="#showcase"
                  className="rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/50 hover:bg-white/5"
                >
                  Watch Footage
                </a>
                <a
                  href="https://drive.google.com/drive/folders/1US8sQDyp60TCfVF0GXDffc9hryI3uLw6?usp=drive_link"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-full border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:border-white/50 hover:bg-white/5"
                >
                  Film Library
                </a>
              </div>
            </FadeIn>
          </div>
        </section>
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </>
  );
}
