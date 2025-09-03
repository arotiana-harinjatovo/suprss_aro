import axios from 'axios';
import API_URL from '../services/api';

const BASE_URL = `${API_URL}/followers`;


export const sendFriendRequest = async (userId, token) => {
  return axios.post(
    `${BASE_URL}/friend-request`,
    { receiver_id: userId },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );
};


export const acceptFriendRequest = (friendshipId, token) =>
  axios.post(`${BASE_URL}/accept-friend/${friendshipId}`, null, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });


export const removeFriend = async (friendshipId, token) => {
  const response = await fetch(`${BASE_URL}/remove-friend/${friendshipId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erreur lors de la suppression.');
  }

  return await response.json();
};


export const followUser = (followedId, token) =>
  axios.post(`${BASE_URL}/follow`, 
    { followed_id: followedId },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    }
  );


export const unfollowUser = async (followId, token) => {
  const response = await fetch(`${API_URL}/unfollow/${followId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erreur lors du désabonnement.');
  }

  return await response.json();
};


