import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../css/shop.css';

function Shop() {
  const [shopItems, setShopItems] = useState([]);
  const [userPoints, setUserPoints] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [purchaseStatus, setPurchaseStatus] = useState(null);
  const navigate = useNavigate();
  
  const API_URL = "http://127.0.0.1:8080/api";

  // Fetch shop items and user points on component mount
  useEffect(() => {
    const fetchShopData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          navigate("/login");
          return;
        }

        // Get shop items
        const itemsResponse = await fetch(`${API_URL}/shop/items`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!itemsResponse.ok) {
          throw new Error(`HTTP error! Status: ${itemsResponse.status}`);
        }
        const itemsData = await itemsResponse.json();
        
        // Get user profile for points
        const profileResponse = await fetch(`${API_URL}/user-profile`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!profileResponse.ok) {
          throw new Error(`HTTP error! Status: ${profileResponse.status}`);
        }
        const profileData = await profileResponse.json();
        
        setShopItems(itemsData);
        setUserPoints(profileData.points);
      } catch (err) {
        setError(err.message);
        console.error("Error fetching shop data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchShopData();
  }, [navigate]);

  const handlePurchase = async (item) => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/login");
        return;
      }

      const response = await fetch(`${API_URL}/shop/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ itemID: item.itemID })
      });

      const result = await response.json();
      
      if (!response.ok) {
        setPurchaseStatus({
          success: false,
          message: result.error || 'Purchase failed'
        });
        return;
      }
      
      // Update UI after successful purchase
      setUserPoints(result.remainingPoints);
      setShopItems(shopItems.map(shopItem => 
        shopItem.itemID === item.itemID 
          ? { ...shopItem, purchased: true } 
          : shopItem
      ));
      
      setPurchaseStatus({
        success: true,
        message: 'Item purchased successfully!'
      });
      
      // Clear status message after 3 seconds
      setTimeout(() => {
        setPurchaseStatus(null);
      }, 3000);
      
    } catch (err) {
      setPurchaseStatus({
        success: false,
        message: err.message
      });
      console.error("Error purchasing item:", err);
    }
  };

  if (loading) {
    return <div className="shop-container loading">Loading shop items...</div>;
  }

  return (
    <div className="shop-container">
      <div className="shop-header">
        <h1>Profile Picture Shop</h1>
        <div className="user-points">
          <span className="points-icon">💰</span>
          <span className="points-value">{userPoints} points</span>
        </div>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      {purchaseStatus && (
        <div className={`purchase-status ${purchaseStatus.success ? 'success' : 'error'}`}>
          {purchaseStatus.message}
        </div>
      )}
      
      <div className="shop-items-grid">
        {shopItems.map((item) => (
          <div key={item.itemID} className="shop-item">
            <img 
              src={item.previewImagePath} 
              alt={item.displayName} 
              className="item-image"
            />
            <div className="item-details">
              <h3>{item.displayName}</h3>
              <p className="item-description">{item.description}</p>
              <div className="item-price">
                <span className="price-icon">💰</span>
                <span className="price-value">{item.pointCost}</span>
              </div>
            </div>
            <div className="item-actions">
              {item.purchased ? (
                <button className="owned-button" disabled>Owned</button>
              ) : (
                <button 
                  className={`purchase-button ${userPoints < item.pointCost ? 'insufficient' : ''}`}
                  onClick={() => handlePurchase(item)}
                  disabled={userPoints < item.pointCost}
                >
                  {userPoints < item.pointCost ? 'Not enough points' : 'Purchase'}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Shop;