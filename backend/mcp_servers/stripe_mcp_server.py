"""
Stripe MCP Server

Model Context Protocol server for Stripe billing integration.
Handles payment processing, subscription management, and billing events.
"""

from typing import Dict, List, Optional, Any
import os
import stripe
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


class StripeMCPServer:
    """
    Stripe MCP Server for billing operations.
    
    Provides methods for:
    - Creating customers
    - Creating subscriptions
    - Processing payments
    - Handling webhooks
    - Retrieving billing history
    """
    
    def __init__(self):
        if not stripe.api_key:
            logger.warning("STRIPE_SECRET_KEY not set - Stripe operations will fail")
        self.stripe = stripe
    
    def create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe customer.
        
        Args:
            email: Customer email
            name: Customer name (optional)
            metadata: Additional metadata (optional)
        
        Returns:
            Stripe customer object
        """
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Stripe customer: {customer.id}")
            
            return {
                "success": True,
                "customer_id": customer.id,
                "customer": customer.to_dict()
            }
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe subscription.
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            metadata: Additional metadata (optional)
        
        Returns:
            Stripe subscription object
        """
        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {}
            )
            
            logger.info(f"Created Stripe subscription: {subscription.id}")
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "subscription": subscription.to_dict()
            }
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_payment_intent(
        self,
        amount: int,  # Amount in cents
        currency: str = "gbp",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent for one-time payment.
        
        Args:
            amount: Amount in cents (e.g., 2500 for £25.00)
            currency: Currency code (default: "gbp")
            customer_id: Stripe customer ID (optional)
            metadata: Additional metadata (optional)
        
        Returns:
            Stripe payment intent object
        """
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                metadata=metadata or {}
            )
            
            logger.info(f"Created payment intent: {intent.id}")
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "payment_intent": intent.to_dict()
            }
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def record_performance_fee(
        self,
        customer_id: str,
        amount: float,  # Amount in currency (e.g., 25.00 for £25.00)
        currency: str = "gbp",
        description: str = "Performance Fee",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Record a performance fee (ACV-based) as an invoice item.
        
        This creates an invoice item that will be charged on the next invoice.
        
        Args:
            customer_id: Stripe customer ID
            amount: Amount in currency (e.g., 25.00)
            currency: Currency code (default: "gbp")
            description: Description for the charge
            metadata: Additional metadata (optional)
        
        Returns:
            Stripe invoice item object
        """
        try:
            # Convert to cents
            amount_cents = int(amount * 100)
            
            invoice_item = self.stripe.InvoiceItem.create(
                customer=customer_id,
                amount=amount_cents,
                currency=currency,
                description=description,
                metadata=metadata or {}
            )
            
            logger.info(f"Created invoice item for performance fee: {invoice_item.id}")
            
            return {
                "success": True,
                "invoice_item_id": invoice_item.id,
                "invoice_item": invoice_item.to_dict()
            }
        except Exception as e:
            logger.error(f"Error recording performance fee: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_customer_subscriptions(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Get all subscriptions for a customer.
        
        Args:
            customer_id: Stripe customer ID
        
        Returns:
            List of subscriptions
        """
        try:
            subscriptions = self.stripe.Subscription.list(
                customer=customer_id,
                limit=100
            )
            
            return {
                "success": True,
                "subscriptions": [sub.to_dict() for sub in subscriptions.data]
            }
        except Exception as e:
            logger.error(f"Error getting customer subscriptions: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_customer_invoices(
        self,
        customer_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get invoice history for a customer.
        
        Args:
            customer_id: Stripe customer ID
            limit: Maximum number of invoices to return
        
        Returns:
            List of invoices
        """
        try:
            invoices = self.stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            return {
                "success": True,
                "invoices": [inv.to_dict() for inv in invoices.data]
            }
        except Exception as e:
            logger.error(f"Error getting customer invoices: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_webhook(
        self,
        payload: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Handle Stripe webhook event.
        
        Args:
            payload: Raw webhook payload (string)
            signature: Stripe signature header
        
        Returns:
            Webhook event data
        """
        try:
            event = self.stripe.Webhook.construct_event(
                payload,
                signature,
                STRIPE_WEBHOOK_SECRET
            )
            
            logger.info(f"Received Stripe webhook: {event['type']}")
            
            # Handle different event types
            event_type = event['type']
            data = event['data']['object']
            
            result = {
                "success": True,
                "event_type": event_type,
                "event_id": event['id'],
                "data": data
            }
            
            # Process specific events
            if event_type == "invoice.payment_succeeded":
                logger.info(f"Invoice payment succeeded: {data.get('id')}")
            elif event_type == "invoice.payment_failed":
                logger.warning(f"Invoice payment failed: {data.get('id')}")
            elif event_type == "customer.subscription.deleted":
                logger.info(f"Subscription cancelled: {data.get('id')}")
            
            return result
            
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            return {
                "success": False,
                "error": "Invalid payload"
            }
        except self.stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            return {
                "success": False,
                "error": "Invalid signature"
            }
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_stripe_mcp_server: Optional[StripeMCPServer] = None

def get_stripe_mcp_server() -> StripeMCPServer:
    """Get singleton Stripe MCP server instance."""
    global _stripe_mcp_server
    if _stripe_mcp_server is None:
        _stripe_mcp_server = StripeMCPServer()
    return _stripe_mcp_server








