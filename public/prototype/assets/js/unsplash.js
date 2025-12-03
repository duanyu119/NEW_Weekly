async function loadHero(selector, query){
  const el = document.querySelector(selector);
  if(!el) return;
  const key = window.UNSPLASH_ACCESS_KEY || null;
  try{
    if(key){
      const r = await fetch(`https://api.unsplash.com/photos/random?query=${encodeURIComponent(query)}&orientation=landscape&content_filter=high`, {
        headers: { Authorization: `Client-ID ${key}` }
      });
      const j = await r.json();
      const url = (j.urls && (j.urls.full || j.urls.regular)) || null;
      if(url){ el.style.backgroundImage = `url(${url}&w=1600)`; return; }
    }
    el.style.backgroundImage = `url(https://source.unsplash.com/random/1600x900?${encodeURIComponent(query)})`;
  }catch{
    el.style.backgroundImage = `url(https://source.unsplash.com/random/1600x900?${encodeURIComponent(query)})`;
  }
}
