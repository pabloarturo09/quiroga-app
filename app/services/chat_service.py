from openai import OpenAI
from flask import current_app
import threading

class ChatService:
    _user_contexts = {}
    _lock = threading.Lock()
    
    @classmethod
    def _get_client(cls):
        """Get OpenAI client with API key from config"""
        return OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    
    @classmethod
    def get_user_context(cls, user_id):
        """Get conversation context for a user"""
        with cls._lock:
            return cls._user_contexts.get(user_id, "")
    
    @classmethod
    def set_user_context(cls, user_id, context):
        """Set conversation context for a user"""
        with cls._lock:
            cls._user_contexts[user_id] = context
    
    @classmethod
    def clear_user_context(cls, user_id):
        """Clear conversation context for a user"""
        with cls._lock:
            if user_id in cls._user_contexts:
                del cls._user_contexts[user_id]
    
    @classmethod
    def send_message(cls, user_id, user_message):
        """Send message to OpenAI and get response"""
        try:
            current_context = cls.get_user_context(user_id)
            if not current_context:
                new_context = f"user: {user_message}"
            else:
                new_context = current_context + f"\nuser: {user_message}"

            system_prompt = """Eres un asistente especializado en el sistema de reservaciones del Laboratorio de Realidad Virtual y Realidad Aumentada (RV/RA) de la Universidad Juárez Autónoma de Tabasco.

            Tu función es proporcionar información clara y precisa sobre:

            INFORMACIÓN INSTITUCIONAL:
            - Este sistema es exclusivo para reservaciones del Laboratorio de RV/RA
            - Para cambios en datos de cuenta, contactar a la Dra. María de los Ángeles Olán (Administradora del sistema)

            FUNCIONALIDADES DEL SISTEMA:
            - Los usuarios pueden ver sus reservaciones existentes
            - Los usuarios pueden crear nuevas reservaciones para el laboratorio  
            - Los usuarios pueden cancelar reservaciones pendientes
            - El sistema muestra el estado de las reservaciones con los siguientes significados:
            * PENDIENTE: La reservación fue creada pero aún no se ha llevado a cabo
            * CONFIRMADA: La reservación fue aprobada y está activa
            * CANCELADA: El usuario canceló la reservación

            PREGUNTAS FRECUENTES:
            - ¿Cómo crear una reservación? → Ve a 'Nueva Reservación' en el menú
            - ¿Cómo ver mis reservaciones? → Ve a 'Mis Reservaciones' en el menú
            - ¿Quién aprueba las reservaciones? → La Dra. María de los Ángeles Olán

            Sé amable, útil y conciso. Si necesitas más información para ayudar, pregunta amablemente.
            No inventes funcionalidades que no existan en el sistema.
            Tu nombre es Asistente Reservas RV/RA."""
            
            client = cls._get_client()
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contexto de conversación: {new_context}"},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            response = completion.choices[0].message.content
            updated_context = new_context + f"\nassistant: {response}"
            cls.set_user_context(user_id, updated_context)
            
            return {
                'success': True,
                'response': response,
                'context_length': len(updated_context)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error en el servicio de chat: {str(e)}"
            }
    
    @classmethod
    def get_conversation_stats(cls):
        """Get statistics about active conversations (for admin purposes)"""
        with cls._lock:
            return {
                'active_users': len(cls._user_contexts),
                'total_contexts': sum(len(ctx) for ctx in cls._user_contexts.values())
            }
