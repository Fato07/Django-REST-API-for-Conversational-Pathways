# Django-REST-API-for-Conversational-Pathways


curl -X POST "https://api.bland.ai/v1/agents" \
     -H "Authorization: sk-nk1owakcjn4wvb9n39m9bo10prehjgqy4gyb4u8xg8ppz7fx8654jxb6e8onda3x69" \
     -H "Content-Type: application/json" \
     -d '{
           "prompt": "Welcome!\nHello, how can I assist you today?",
           "voice": "default_voice",
           "analysis_schema": {},
           "metadata": {},
           "pathway_id": "",
           "language": "ENG",
           "model": "enhanced",
           "first_sentence": "",
           "tools": [{}],
           "dynamic_data": {},
           "interruption_threshold": 100,
           "max_duration": 30
         }'


curl --request POST \
  --url https://api.bland.ai/v1/agents \
  --header 'Content-Type: application/json' \
  --header 'authorization: sk-nk1owakcjn4wvb9n39m9bo10prehjgqy4gyb4u8xg8ppz7fx8654jxb6e8onda3x69' \
  --data '{
  "prompt": "Welcome!\nHello, how can I assist you today?"
}'