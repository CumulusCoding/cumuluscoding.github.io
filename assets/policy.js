// Policy page functionality
class PolicyPage {
  constructor() {
    this.policy = null;
    this.init();
  }

  init() {
    // Update year in footer
    document.getElementById("year").textContent = new Date().getFullYear();
    
    // Get parameters from URL
    const params = this.getQueryParams();
    const app = params.app;
    const type = params.type;
    
    if (!app || !type) {
      this.showError('Missing required parameters: app and type');
      return;
    }
    
    // Load and render policy
    this.loadPolicy(app, type);
  }

  getQueryParams() {
    const params = new URLSearchParams(window.location.search);
    return {
      app: params.get('app'),
      type: params.get('type')
    };
  }

  async loadPolicy(app, type) {
    try {
      const response = await fetch(`data/policies/${app}/${type}.json`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      this.policy = await response.json();
      this.renderPolicy();
      
    } catch (error) {
      console.error('Error loading policy:', error);
      this.showError('Failed to load policy. Please try again later.');
    }
  }

  renderPolicy() {
    if (!this.policy) {
      this.showError('No policy data available');
      return;
    }

    // Hide loading, show content
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('policy-content').classList.remove('hidden');

    // Update page title
    document.getElementById('page-title').textContent = `${this.policy.title} - Cumulus Coding`;

    // Update policy header
    document.getElementById('policy-title').textContent = this.policy.title;
    document.getElementById('app-name').textContent = this.policy.appId;
    
    // Format and display the last updated date
    const lastUpdated = this.policy.metadata?.lastUpdated || this.policy.lastUpdated;
    if (lastUpdated) {
      const formattedDate = this.formatDate(lastUpdated);
      document.getElementById('update-date').textContent = formattedDate;
    }

    // Update app icon if available
    this.updateAppIcon(this.policy.appId);

    // Render table of contents
    this.renderTableOfContents();

    // Render policy sections
    this.renderSections();

    // Update contact information
    this.updateContactInfo();
  }

  updateAppIcon(appId) {
    const iconContainer = document.getElementById('app-icon');
    const iconPath = `assets/apps/${appId}/icon.png`;
    
    // Try to load the actual app icon
    const img = new Image();
    img.onload = function() {
      iconContainer.innerHTML = '';
      iconContainer.classList.remove('bg-gradient-to-br', 'from-blue-500', 'to-purple-600');
      iconContainer.classList.add('bg-white', 'p-1');
      iconContainer.appendChild(img);
      img.className = 'w-full h-full rounded-xl object-cover';
    };
    img.onerror = function() {
      // Fallback to default SVG icon
      iconContainer.classList.add('bg-gradient-to-br', 'from-blue-500', 'to-purple-600');
      iconContainer.classList.remove('bg-white', 'p-1');
      iconContainer.innerHTML = `
        <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      `;
    };
    img.src = iconPath;
  }

  renderTableOfContents() {
    const tocList = document.getElementById('toc-list');
    const sections = this.policy.sections;
    
    if (sections.length <= 1) {
      // Hide TOC if there's only one section
      document.getElementById('toc').classList.add('hidden');
      return;
    }
    
    const tocItems = sections.map((section, index) => {
      const sectionId = this.generateSectionId(section.heading);
      return `
        <a href="#${sectionId}" 
           class="block text-gray-700 hover:text-primary transition-colors py-1">
          ${index + 1}. ${section.heading}
        </a>
      `;
    }).join('');
    
    tocList.innerHTML = tocItems;
  }

  renderSections() {
    const sectionsContent = document.getElementById('sections-content');
    const sections = this.policy.sections;
    
    const sectionsHtml = sections.map((section, index) => {
      const sectionId = this.generateSectionId(section.heading);
      const contentHtml = this.renderSectionContent(section.content);
      
      return `
        <section id="${sectionId}" class="mb-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">
            ${index + 1}. ${section.heading}
          </h2>
          <div class="section-content">
            ${contentHtml}
          </div>
        </section>
      `;
    }).join('');
    
    sectionsContent.innerHTML = sectionsHtml;
  }

  renderSectionContent(content) {
    return content.map(item => {
      // Check if it's a list item
      if (item.startsWith('- ') || item.startsWith('* ')) {
        return `<li>${item.substring(2)}</li>`;
      }
      
      // Check if it's a numbered list item
      const numberedMatch = item.match(/^(\d+)\.\s+(.+)$/);
      if (numberedMatch) {
        return `<li>${numberedMatch[2]}</li>`;
      }
      
      // Check if it contains list items
      if (item.includes('\n    - ')) {
        const parts = item.split('\n    - ');
        const paragraph = parts[0];
        const listItems = parts.slice(1).map(item => `<li>${item.trim()}</li>`).join('');
        
        return `
          <p>${paragraph}</p>
          <ul>${listItems}</ul>
        `;
      }
      
      // Regular paragraph
      return `<p>${item}</p>`;
    }).join('');
  }

  generateSectionId(heading) {
    return heading
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  }

  updateContactInfo() {
    if (this.policy.contact && this.policy.contact.email) {
      const contactEmail = document.getElementById('contact-email');
      contactEmail.href = `mailto:${this.policy.contact.email}`;
      contactEmail.textContent = this.policy.contact.email;
    }
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleDateString('en-GB', { month: 'long' });
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  }

  showError(message) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('error').classList.remove('hidden');
    
    const errorMessage = document.querySelector('#error p');
    if (errorMessage) {
      errorMessage.textContent = message;
    }
  }
}

// Initialize the policy page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PolicyPage();
});
