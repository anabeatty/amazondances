import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Save, X } from 'lucide-react';
import './App.css'; // Importe o arquivo CSS aqui!

const API_BASE = 'http://127.0.0.1:5000/api';

const App = () => {
  const [categories, setCategories] = useState([]);
  const [pages, setPages] = useState([]);
  const [collaborators, setCollaborators] = useState([]);
  const [activeCategory, setActiveCategory] = useState(null);
  const [activePage, setActivePage] = useState(null);
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [showAddPage, setShowAddPage] = useState(false);
  const [editingPage, setEditingPage] = useState(null);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newPage, setNewPage] = useState({ title: '', content: '', category_id: '' });

  // Fetch data from API
  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/categories`);
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('Error fetching categories:', error);
      // Fallback demo data
      setCategories([
        { id: 1, name: 'Our rhythms', pages: [{ id: 1, title: 'General History' }, { id: 2, title: 'Carimbó' }] },
        { id: 2, name: 'Classes', pages: [{ id: 3, title: 'Beginner Classes' }] },
        { id: 3, name: 'Performances', pages: [{ id: 4, title: 'Recent Performances' }] }
      ]);
    }
  };

  const fetchPages = async () => {
    try {
      const response = await fetch(`${API_BASE}/pages`);
      const data = await response.json();
      setPages(data);
    } catch (error) {
      console.error('Error fetching pages:', error);
      // Fallback demo data
      setPages([
        { id: 1, title: 'General History', content: '<h2>General History</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. This is the history of our dance group...</p>', category_id: 1 },
        { id: 2, title: 'Carimbó', content: '<h2>Carimbó</h2><p>Carimbó is a traditional dance from Northern Brazil...</p>', category_id: 1 },
        { id: 3, title: 'Beginner Classes', content: '<h2>Beginner Classes</h2><p>Join our beginner-friendly classes every Tuesday and Thursday...</p>', category_id: 2 },
        { id: 4, title: 'Recent Performance', content: '<h2>Recent performance</h2><p>Check out our latest performances and upcoming events...</p>', category_id: 3 }
      ]);
    }
  };

  const fetchCollaborators = async () => {
    try {
      const response = await fetch(`${API_BASE}/collaborators`);
      const data = await response.json();
      setCollaborators(data);
    } catch (error) {
      console.error('Error fetching collaborators:', error);
      setCollaborators([{ id: 1, username: 'admin' }]);
    }
  };

  useEffect(() => {
    fetchCategories();
    fetchPages();
    fetchCollaborators();
  }, []);

  // Add new category
  const handleAddCategory = async () => {
    if (!newCategoryName.trim()) return;
    
    try {
      const response = await fetch(`${API_BASE}/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCategoryName })
      });
      
      if (response.ok) {
        fetchCategories();
        setNewCategoryName('');
        setShowAddCategory(false);
      }
    } catch (error) {
      // Fallback for demo
      const newId = Math.max(...categories.map(c => c.id), 0) + 1;
      setCategories([...categories, { id: newId, name: newCategoryName, pages: [] }]);
      setNewCategoryName('');
      setShowAddCategory(false);
    }
  };

  // Add new page
  const handleAddPage = async () => {
    if (!newPage.title.trim() || !newPage.content.trim() || !newPage.category_id) return;
    
    try {
      const response = await fetch(`${API_BASE}/pages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newPage,
          collaborator_id: collaborators[0]?.id || 1
        })
      });
      
      if (response.ok) {
        fetchPages();
        fetchCategories();
        setNewPage({ title: '', content: '', category_id: '' });
        setShowAddPage(false);
      }
    } catch (error) {
      // Fallback for demo
      const newId = Math.max(...pages.map(p => p.id), 0) + 1;
      const newPageObj = { id: newId, ...newPage, collaborator_id: 1 };
      setPages([...pages, newPageObj]);
      
      // Update categories
      setCategories(categories.map(cat => 
        cat.id === parseInt(newPage.category_id) 
          ? { ...cat, pages: [...cat.pages, { id: newId, title: newPage.title }] }
          : cat
      ));
      
      setNewPage({ title: '', content: '', category_id: '' });
      setShowAddPage(false);
    }
  };

  // Update page
  const handleUpdatePage = async (pageId, updatedData) => {
    try {
      const response = await fetch(`${API_BASE}/pages/${pageId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
      });
      
      if (response.ok) {
        fetchPages();
        fetchCategories();
        setEditingPage(null);
      }
    } catch (error) {
      // Fallback for demo
      setPages(pages.map(p => p.id === pageId ? { ...p, ...updatedData } : p));
      setEditingPage(null);
    }
  };

  // Delete page
  const handleDeletePage = async (pageId) => {
    if (!confirm('Are you sure you want to delete this page?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/pages/${pageId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchPages();
        fetchCategories();
        setActivePage(null);
      }
    } catch (error) {
      // Fallback for demo
      setPages(pages.filter(p => p.id !== pageId));
      setCategories(categories.map(cat => ({
        ...cat,
        pages: cat.pages.filter(p => p.id !== pageId)
      })));
      setActivePage(null);
    }
  };

  const getCurrentPage = () => {
    return pages.find(p => p.id === activePage);
  };

  return (
    <div className="app-container">
      {/* Header Navigation */}
      <nav className="main-nav">
        <div className="main-nav-inner">
          <div
            onClick={() => { setActivePage(null); setActiveCategory(null); }}
            className={`nav-item ${!activePage && !activeCategory ? 'active-home' : ''}`}
          >
            Home
          </div>
          
          {categories.map((category) => (
            <div 
              key={category.id} 
              className="dropdown-container"
              onMouseEnter={() => setActiveCategory(category.id)}
              onMouseLeave={() => setActiveCategory(null)}
            >
              <div
                className={`nav-item ${activeCategory === category.id ? 'active' : ''}`}
              >
                {category.name}
                
                {/* Dropdown Menu */}
                {activeCategory === category.id && (
                  <div className="dropdown-menu">
                    {category.pages?.map((page) => (
                      <div
                        key={page.id}
                        onClick={() => {
                          setActivePage(page.id);
                          setActiveCategory(null);
                        }}
                        className="dropdown-item"
                      >
                        {page.title}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {/* Admin Controls */}
          <div className="admin-controls">
            <button
              onClick={() => setShowAddCategory(true)}
              className="admin-button"
            >
              <Plus size={16} /> Category
            </button>
            <button
              onClick={() => setShowAddPage(true)}
              className="admin-button"
            >
              <Plus size={16} /> Page
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="main-content">
        {!activePage ? (
          // Home Page
          <div>
            <h1 className="home-title">
              The Project
            </h1>
            <p className="home-description">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
            </p>
            
            {/* Category Preview Cards */}
            <div className="category-cards-grid">
              {categories.map((category, index) => {
                const colorsClass = `color-${(index % 4) + 1}`; // Cycle through 4 defined colors
                return (
                  <div
                    key={category.id}
                    className={`category-card ${colorsClass}`}
                    onClick={() => setActiveCategory(category.id)}
                  >
                    <h3>{category.name}</h3>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          // Page Content
          <div>
            {editingPage === activePage ? (
              // Edit Mode
              <div>
                <div className="edit-form-actions">
                  <input
                    type="text"
                    value={editingPage.title || getCurrentPage()?.title || ''}
                    onChange={(e) => setEditingPage({...editingPage, title: e.target.value})}
                    className="form-input large"
                  />
                  <button
                    onClick={() => handleUpdatePage(activePage, editingPage)}
                    className="button primary button-md"
                  >
                    <Save size={16} /> Save
                  </button>
                  <button
                    onClick={() => setEditingPage(null)}
                    className="button secondary button-md"
                  >
                    <X size={16} /> Cancel
                  </button>
                </div>
                <textarea
                  value={editingPage.content || getCurrentPage()?.content || ''}
                  onChange={(e) => setEditingPage({...editingPage, content: e.target.value})}
                  className="form-textarea"
                  placeholder="Enter HTML content here..."
                />
              </div>
            ) : (
              // View Mode
              <div>
                <div className="page-header">
                  <h1 className="page-title">
                    {getCurrentPage()?.title}
                  </h1>
                  <div className="page-actions">
                    <button
                      onClick={() => setEditingPage(getCurrentPage())}
                      className="button primary button-sm"
                    >
                      <Edit size={16} /> Edit
                    </button>
                    <button
                      onClick={() => handleDeletePage(activePage)}
                      className="button danger button-sm"
                    >
                      <Trash2 size={16} /> Delete
                    </button>
                  </div>
                </div>
                
                <div
                  className="page-content-display"
                  dangerouslySetInnerHTML={{ __html: getCurrentPage()?.content || '' }}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add Category */}
      {showAddCategory && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 className="modal-title">Add New Category</h3>
            <input
              type="text"
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
              placeholder="Category name"
              className="form-input"
            />
            <div className="modal-actions">
              <button
                onClick={() => setShowAddCategory(false)}
                className="button neutral button-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleAddCategory}
                className="button primary button-lg"
              >
                Add Category
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Page*/}
      {showAddPage && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 className="modal-title">Add New Page</h3>
            
            <input
              type="text"
              value={newPage.title}
              onChange={(e) => setNewPage({...newPage, title: e.target.value})}
              placeholder="Page title"
              className="form-input"
            />
            
            <select
              value={newPage.category_id}
              onChange={(e) => setNewPage({...newPage, category_id: e.target.value})}
              className="form-input"
            >
              <option value="">Select a category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>{cat.name}</option>
              ))}
            </select>
            
            <textarea
              value={newPage.content}
              onChange={(e) => setNewPage({...newPage, content: e.target.value})}
              placeholder="Page content (HTML supported)"
              className="form-textarea"
            />
            
            <div className="modal-actions">
              <button
                onClick={() => setShowAddPage(false)}
                className="button neutral button-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleAddPage}
                className="button primary button-lg"
              >
                Add Page
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;