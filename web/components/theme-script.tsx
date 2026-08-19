export function ThemeScript() {
  const code = `(function(){try{var t=localStorage.getItem("biblia:theme");if(t==="dark")document.documentElement.classList.add("dark");}catch(e){}})();`
  return <script dangerouslySetInnerHTML={{ __html: code }} />
}
