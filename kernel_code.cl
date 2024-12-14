
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

kernel void intersect(global Ray *rays, global Object *objects, int amObjects, global float3 *result){
    int id = get_global_id(0);
    Ray ray = rays[id];

    float min_dist = INFINITY;
    float3 color = (float3)(0, 0, 0);
    for(int i = 0; i<amObjects; i++){
        Object object = objects[i];
        float dist = -1;
        if(object.type == 0) dist = intersect_sphere(ray, object.center, object.radius);
        else if(object.type == 1) dist = intersect_plane(ray, object.normal, object.distance);
        if(dist <1e-8) continue;
        if(dist<min_dist){
            min_dist = dist;
            color = object.color;
        }
    }
    result[id] = color;
}

// kernel void intersect(global Ray *rays, global Object *objects, int amObjects, global float4 *result){
//     int id = get_global_id(0);
//     if(id == 0) printf("Ray: (%f, %f, %f)\n", rays[0].direction.x, rays[0].direction.y, rays[0].direction.z);
//     if(id == 0) printf("Ray: (%f, %f, %f)\n", rays[1].direction.x, rays[1].direction.y, rays[1].direction.z);
//     if(id == 0) printf("Ray: (%f, %f, %f)\n", rays[2].direction.x, rays[2].direction.y, rays[2].direction.z);
//     result[id] = (float4)(objects[0].color, 0); 
// }
