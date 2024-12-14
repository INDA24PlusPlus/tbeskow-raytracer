typedef struct{
    float3 origin;
    float3 direction;
} Ray;

typedef struct{
    int type;
    float luminance;
    float radius;
    float distance;
    float3 color;
    float3 emittedColor;

    float3 center;

    float3 normal;
} Object;


float intersect_plane(Ray ray, float3 N, float distance){
    float scalar = dot(ray.direction, N);
    if(scalar == 0) return -1;
    return (distance-dot(ray.origin, N))/scalar;
}

float intersect_sphere(Ray ray, float3 Os, float r){
    float3 v = ray.origin-Os;
    float a = dot(ray.direction, ray.direction);
    float b = 2*dot(v, ray.direction);
    float c = dot(v, v)-r*r;

    float toRoot = b*b-4*a*c;
    if(toRoot < 0) return -1;
    return (-b-sqrt(toRoot))/(2*a);
}

float2 intersect(Ray ray, global Object *objects, int amObjects){

    float min_dist = INFINITY;
    int min_index = -1;
    for(int i = 0; i<amObjects; i++){
        Object object = objects[i];
        float dist = -1;
        if(object.type == 0) dist = intersect_sphere(ray, object.center, object.radius);
        else if(object.type == 1) dist = intersect_plane(ray, object.normal, object.distance);
        if(dist <1e-8) continue;
        if(dist<min_dist){
            min_dist = dist;
            min_index = i;
        }
    }
    return (float2)(min_index, min_dist);
}

float randomValue(uint state){ // borde kanske testa (igentligen ska state ut till nästa test)
    state = state * 747796405 + 2891336453;
    uint result = ((state >> ((state>>28)+4)) ^ state) * 277803737;
    result = (result >> 22) ^ result;
    return ((float)result / (float)UINT_MAX-0.5)*2.;
}

float3 randomDirection(float3 normal, uint state){
    while(true){
        state = state*747796405 + 2891336453;
        float3 direction = (float3)(randomValue(state), randomValue(state+1), randomValue(state+2));
        if(length(direction)>1) continue;
        if(dot(direction, normal) < 0) continue;
        return normalize(direction);
    }
}

float3 findNormal(float3 origin, global Object *objects, int index){
    if(objects[index].type == 0) return normalize(origin-objects[index].center);
    else if(objects[index].type == 1) return  objects[index].normal;

    return (float3)(0, 0, 0);
}


kernel void trace(global Ray *rays, global Object *objects, int amObjects, int depth, int amount, uint state, global float4 *result){
    int id = get_global_id(0);
    Ray ray = rays[id];

    float3 res = (float3)(0, 0, 0);
    Ray originalRay = ray;
    for(int iteration = 0; iteration<amount; iteration++){
        float3 incomingColor = (float3)(0, 0, 0);
        float3 rayColor = (float3)(1, 1, 1);
        ray = originalRay;

        for(int i = 0; i<depth; i++){
            float2 intersection = intersect(ray, objects, amObjects);
            int index = intersection.x;
            float distance = intersection.y;
            if(index == -1){
                incomingColor += rayColor*0.1f;
                break;
            }
            ray.origin += ray.direction*distance;
            ray.direction = randomDirection(findNormal(ray.origin, objects, index), id*depth*2+i+iteration*291383+state);

            incomingColor+=objects[index].color*objects[index].luminance*rayColor;
            rayColor *= objects[index].color;
        }
        res += incomingColor;
    }

    result[id] += (float4)(res, 0);
}

