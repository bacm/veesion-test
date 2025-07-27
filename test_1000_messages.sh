for i in {1..1000}; do
    curl -X POST "http://$(minikube ip):30000/alert" \
        -H "Content-Type: application/json" \
        -d '{
            "uid": "E00E9901-9246-4869-945A-7A0AABE1C382",
            "video": "/videos/test_1.avi",
            "timestamp": 1748871320.6882,
            "store": "test-store"
        }' &
done

wait