from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CollectionMessage, CollectionMember, User
from app.schemas.chat import CollectionMessageCreate, CollectionMessageResponse
from app.services.auth import get_current_user   
from datetime import datetime, timedelta
import json

router = APIRouter(tags=["Messages"])

active_connections = {}

@router.websocket("/ws/collections/{collection_id}/chat")
async def chat_websocket(
    websocket: WebSocket,
    collection_id: int,
    db: Session = Depends(get_db),
    token: str = Query(...),
):
    # Authentifie l'utilisateur via le token
    try:
        current_user = get_current_user(token, db)
    except Exception as e:
        await websocket.close(code=1008)
        print("❌ Authentification échouée :", e)
        return
    await websocket.accept()
    print(f"✅ Connexion WebSocket reçue pour la collection {collection_id} par {current_user.username}")

    if collection_id not in active_connections:
        active_connections[collection_id] = []
    active_connections[collection_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            print("📩 Message brut reçu :", data)

            try:
                message_data = CollectionMessageCreate.parse_raw(data)
            except Exception as e:
                print("❌ Erreur de parsing :", e)
                await websocket.send_text(json.dumps({"error": "Format de message invalide"}))
                continue

            # Vérifie que l'utilisateur est bien membre de la collection
            is_member = db.query(CollectionMember).filter_by(
                collection_id=collection_id,
                user_id=current_user.id
            ).first()

            if not is_member:
                print("⚠️ Utilisateur non membre :", current_user.id)
                await websocket.send_text(json.dumps({
                    "error": "Vous n'avez pas accès à cette discussion."
                }))
                continue

            # Sauvegarde du message
            new_message = CollectionMessage(
                collection_id=collection_id,
                user_id=current_user.id,
                content=message_data.content,
                timestamp=datetime.utcnow()
            )

            try:
                db.add(new_message)
                db.commit()
                print("✅ Message enregistré :", new_message.content)
            except Exception as e:
                print("❌ Erreur lors de l'enregistrement :", e)
                await websocket.send_text(json.dumps({"error": "Erreur serveur"}))
                continue

            # Diffusion à tous les clients connectés
            for conn in active_connections[collection_id]:
                await conn.send_text(json.dumps({
                    "user_id": current_user.id,
                    "user_name": current_user.username,
                    "content": new_message.content,
                    "timestamp": new_message.timestamp.isoformat()
                }))

    except WebSocketDisconnect:
        print(f"🔌 Déconnexion WebSocket pour collection {collection_id}")
        active_connections[collection_id].remove(websocket)

    except Exception as e:
        print("❌ Erreur inattendue :", e)
        active_connections[collection_id].remove(websocket)



@router.get("/ws/collections/{collection_id}/messages", response_model=list[CollectionMessageResponse])
def get_recent_messages(
    collection_id: int, 
    db: Session = Depends(get_db),
    
    ):
    since = datetime.utcnow() - timedelta(days=1)

    messages = (
        db.query(CollectionMessage)
        .filter(CollectionMessage.collection_id == collection_id)
        .filter(CollectionMessage.timestamp >= since)
        .order_by(CollectionMessage.timestamp.asc())
        .all()
    )

    response = []
    for msg in messages:
        user = db.query(User).filter(User.id == msg.user_id).first()
        response.append(CollectionMessageResponse(
            user_id=msg.user_id,
            user_name=user.username if user else f"Utilisateur {msg.user_id}",
            content=msg.content,
            timestamp=msg.timestamp
        ))

    return response

