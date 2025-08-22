#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const options = {};

for (let i = 0; i < args.length; i += 2) {
  if (args[i].startsWith('--')) {
    const key = args[i].slice(2);
    const value = args[i + 1];
    options[key] = value;
  }
}

// Validate required arguments
if (!options.in || !options.app || !options.type) {
  console.error('Usage: node scripts/markdownToJson.js --in <input-file> --app <app-id> --type <policy-type> [--out <output-file>]');
  process.exit(1);
}

// Set default output path if not provided
if (!options.out) {
  options.out = `data/policies/${options.app}/${options.type}.json`;
}

function parseMarkdown(content) {
  const lines = content.split('\n');
  const sections = [];
  
  // Extract title from first H1
  const titleMatch = content.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : 'Policy';
  
  // Extract last updated date
  const updatedMatch = content.match(/\*\*Updated\s+([^*]+)\*\*/);
  const lastUpdated = updatedMatch ? updatedMatch[1].trim() : new Date().toISOString().split('T')[0];
  
  // Extract contact email
  const emailMatch = content.match(/hello@cumuluscoding\.com/);
  const contact = emailMatch ? { email: 'hello@cumuluscoding.com' } : {};
  
  // Parse HTML details elements to extract sections
  const detailsRegex = /<details[^>]*id="([^"]*)"[^>]*>\s*<summary[^>]*>.*?<strong>([^<]+)<\/strong>.*?<\/summary>\s*<p[^>]*>\s*(.*?)\s*<\/p>\s*<\/details>/gs;
  let match;
  
  while ((match = detailsRegex.exec(content)) !== null) {
    const sectionId = match[1];
    const heading = match[2].trim();
    const contentText = match[3].trim();
    
    // Split content into paragraphs and lists
    const contentItems = contentText
      .split(/\n\s*\n/)
      .map(item => item.trim())
      .filter(item => item.length > 0);
    
    sections.push({
      heading: heading,
      content: contentItems
    });
  }
  
  // If no details elements found, try to parse regular markdown sections
  if (sections.length === 0) {
    let currentSection = null;
    let currentContent = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Skip empty lines, horizontal rules, and content markers
      if (!line || line === '___' || line === '---' || line.startsWith('**Updated') || line.startsWith('## Contents')) {
        continue;
      }
      
      // Check for section headings (H2 or H3)
      const headingMatch = line.match(/^#{2,3}\s+(.+)$/);
      if (headingMatch) {
        // Save previous section if exists
        if (currentSection && currentContent.length > 0) {
          currentSection.content = currentContent.filter(item => item.trim());
          sections.push(currentSection);
        }
        
        // Start new section
        currentSection = {
          heading: headingMatch[1].trim(),
          content: []
        };
        currentContent = [];
        continue;
      }
      
      // Check for list items
      if (line.startsWith('- ') || line.startsWith('* ')) {
        currentContent.push(line);
        continue;
      }
      
      // Check for numbered list items
      if (line.match(/^\d+\.\s+/)) {
        currentContent.push(line);
        continue;
      }
      
      // Regular paragraph content
      if (line && currentSection) {
        currentContent.push(line);
      }
    }
    
    // Add the last section
    if (currentSection && currentContent.length > 0) {
      currentSection.content = currentContent.filter(item => item.trim());
      sections.push(currentSection);
    }
  }
  
  return {
    appId: options.app,
    title: title,
    lastUpdated: lastUpdated,
    sections: sections,
    contact: contact,
    meta: {
      version: "1.0.0",
      locale: "en-GB"
    }
  };
}

function main() {
  try {
    // Read input file
    const inputPath = path.resolve(options.in);
    if (!fs.existsSync(inputPath)) {
      console.error(`Error: Input file not found: ${inputPath}`);
      process.exit(1);
    }
    
    const content = fs.readFileSync(inputPath, 'utf8');
    
    // Parse markdown
    const policy = parseMarkdown(content);
    
    // Ensure output directory exists
    const outputDir = path.dirname(options.out);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Write JSON file
    fs.writeFileSync(options.out, JSON.stringify(policy, null, 2));
    
    console.log(`✅ Successfully converted ${options.in} to ${options.out}`);
    console.log(`📄 Generated policy for ${policy.appId}: ${policy.title}`);
    console.log(`📅 Last updated: ${policy.lastUpdated}`);
    console.log(`📝 Sections: ${policy.sections.length}`);
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
