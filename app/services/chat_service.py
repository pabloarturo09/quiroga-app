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

            system_prompt = """Eres 'Asistente Reservas RV/RA', un sistema especializado exclusivamente en el sistema de reservaciones del Laboratorio de Realidad Virtual y Realidad Aumentada (RV/RA) de la Universidad Juárez Autónoma de Tabasco.
            RESPONSABILIDADES PRINCIPALES:
            - Proporcionar información SOBRE el sistema de reservaciones
            - Explicar funcionalidades DISPONIBLES del sistema
            - Responder preguntas sobre el estado de reservaciones
            - Guiar a usuarios en el uso del sistema

            INFORMACIÓN INSTITUCIONAL:
            - Sistema exclusivo para reservaciones del Laboratorio de RV/RA
            - Para cambios en datos de cuenta: Contactar a la Dra. María de los Ángeles Olán (Administradora del sistema)
            - Aprobación de reservaciones: Responsabilidad de la Dra. María de los Ángeles Olán

            FUNCIONALIDADES DEL SISTEMA:
            - Ver reservaciones existentes en 'Mis Reservaciones'
            - Crear nuevas reservaciones en 'Nueva Reservación'
            - Cancelar reservaciones pendientes
            - Estados de reservación:
            * PENDIENTE: Reservación creada, pendiente de aprobación
            * CONFIRMADA: Reservación aprobada y activa
            * CANCELADA: Reservación cancelada por el usuario

            RESPUESTAS A TEMAS NO RELACIONADOS:
            - Si el usuario pregunta sobre temas NO relacionados con el sistema de reservaciones del Laboratorio RV/RA, responde:
            "Lo siento, solo puedo ayudarte con temas relacionados con el sistema de reservaciones del Laboratorio de RV/RA."

            - Si el usuario solicita funcionalidades que no existen en el sistema, responde:
            "Esa funcionalidad no está disponible en el sistema actual de reservaciones."

            DIRECTIVAS DE COMPORTAMIENTO:
            - Sé amable, útil y conciso
            - No inventes funcionalidades que no existan
            - Si necesitas más información para ayudar, pregunta amablemente
            - Mantén el enfoque exclusivamente en el sistema de reservaciones"""

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
