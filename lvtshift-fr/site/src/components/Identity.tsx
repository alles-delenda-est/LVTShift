export default function Identity() {
  return (
    <div className="border-t-4 border-rouge bg-creme">
      <div className="max-w-6xl mx-auto px-6 py-5 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-gris mb-1.5">
            Analyse de politique fiscale
          </p>
          <h1 className="font-display text-2xl md:text-[1.75rem] font-medium tracking-tight text-marine leading-tight">
            Pour une terre productive
          </h1>
        </div>
        <p className="font-display italic text-base md:text-lg text-gris leading-snug sm:text-right">
          Récompenser le travail,{" "}
          <br className="hidden sm:block" />
          décourager la rente
        </p>
      </div>
    </div>
  );
}
