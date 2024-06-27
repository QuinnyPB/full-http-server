// template for header component
// const headerTemplate = document.createElement("header-template");
// headerTemplate.innerHTML = `
//   <header class="header-header">
//     <nav>
//       <a href="/index.html">Home</a>
//       <a href="/pages/about.html">About</a>
//       <a href="/pages/resources.html">Resources</a>
//       <a href="/pages/projects.html">Projects</a>
//     </nav>
//   </header>
// `;
// document.body.appendChild(headerTemplate);

// template for header component
class Header extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {
    this.innerHTML = `<header class="header-header">
      <nav>
        <a href="/index.html">Home</a>
        <a href="/pages/about.html">About</a>
        <a href="/pages/resources.html">Resources</a>
        <a href="/pages/projects.html">Projects</a>
        <a href="/pages/logs.html">Logs</a>
        <a href="/pages/dir.html">Directories</a>
      </nav>
    </header>`;
  }
}

customElements.define("header-component", Header);
