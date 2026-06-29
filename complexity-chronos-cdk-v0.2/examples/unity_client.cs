/**
 * Chronos CDK - Unity Client Example
 * ====================================
 * Drop this script on a GameObject in your Unity scene.
 * It polls the Chronos engine and applies NPC intents.
 *
 * Setup:
 *   1. Start Chronos engine: python -m engine
 *   2. Attach this script to a manager GameObject
 *   3. Assign your NPC GameObjects to the npcs array
 *
 * Requirements:
 *   - Unity 2020.3+
 *   - Newtonsoft.Json (via Package Manager)
 */

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json.Linq;

public class ChronosClient : MonoBehaviour
{
    [Header("Chronos Engine")]
    public string engineUrl = "http://localhost:5000";
    public float pollInterval = 1.0f;

    [Header("Player")]
    public Transform playerTransform;
    public bool isArmed = false;
    public bool isGifting = false;
    public int killCount = 0;

    [Header("NPCs")]
    public ChronosNPC[] npcs;

    private float _nextPoll = 0f;

    void Update()
    {
        if (Time.time >= _nextPoll)
        {
            _nextPoll = Time.time + pollInterval;
            StartCoroutine(PollEngine());
        }
    }

    IEnumerator PollEngine()
    {
        // 1. Send player state
        yield return SendPlayerState();

        // 2. Get engine state
        using (var request = UnityWebRequest.Get($"{engineUrl}/api/game/state"))
        {
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                var state = JObject.Parse(request.downloadHandler.text);
                ApplyNPCIntents(state);
            }
            else
            {
                Debug.LogWarning($"[Chronos] Engine error: {request.error}");
            }
        }
    }

    IEnumerator SendPlayerState()
    {
        var body = new JObject
        {
            ["armed"] = isArmed,
            ["gift_active"] = isGifting,
            ["kills"] = killCount,
            ["x"] = playerTransform ? playerTransform.position.x / 100f : 0.5f,
            ["y"] = playerTransform ? playerTransform.position.z / 100f : 0.5f,
        };

        var request = new UnityWebRequest($"{engineUrl}/api/arena/player", "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(body.ToString());
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();
    }

    void ApplyNPCIntents(JObject state)
    {
        var npcsData = state["npcs"] as JObject;
        if (npcsData == null) return;

        foreach (var npc in npcs)
        {
            if (npc == null) continue;
            var data = npcsData[npc.npcId] as JObject;
            if (data == null) continue;

            npc.intent = data["intent"]?.ToString() ?? "idle";
            npc.coalition = data["coalition"]?.ToString() ?? "neutral";
            npc.isLeader = data["is_leader"]?.ToObject<bool>() ?? false;
            npc.trust = data["trust"]?.ToObject<float>() ?? 0f;
            npc.fear = data["fear"]?.ToObject<float>() ?? 0f;
            npc.anger = data["anger"]?.ToObject<float>() ?? 0f;
            npc.loyalty = data["loyalty"]?.ToObject<float>() ?? 0f;
            npc.grief = data["grief"]?.ToObject<float>() ?? 0f;
        }
    }

    // Call this when player kills an NPC
    public void OnNPCKilled()
    {
        killCount++;
        StartCoroutine(SendPlayerState());
    }

    // Call this when player offers a gift
    public void OnGiftOffered()
    {
        isGifting = true;
        StartCoroutine(SendPlayerState());
        Invoke(nameof(StopGifting), 3f);
    }

    void StopGifting() { isGifting = false; }
}

/**
 * Attach this to each NPC GameObject.
 * The ChronosClient will update these fields every poll.
 */
public class ChronosNPC : MonoBehaviour
{
    [Header("Identity")]
    public string npcId = "A1"; // Must match engine ID

    [Header("State (Updated by Engine)")]
    public string intent = "idle";
    public string coalition = "neutral";
    public bool isLeader = false;

    [Header("Emotions (Updated by Engine)")]
    public float trust = 0f;
    public float fear = 0f;
    public float anger = 0f;
    public float loyalty = 0f;
    public float grief = 0f;

    [Header("Movement")]
    public float moveSpeed = 3f;
    public Transform playerTarget;

    void Update()
    {
        // Apply intent as movement behavior
        switch (intent)
        {
            case "attack":
                MoveToward(playerTarget.position, moveSpeed * 1.5f);
                break;
            case "flee":
                MoveAway(playerTarget.position, moveSpeed * 1.8f);
                break;
            case "guard":
                MoveToward(playerTarget.position + GetGuardOffset(), moveSpeed);
                break;
            case "orbit":
                OrbitAround(playerTarget.position, 5f, moveSpeed);
                break;
            case "curious":
                MoveToward(playerTarget.position, moveSpeed * 0.5f, stopDistance: 3f);
                break;
            default:
                // idle - small random movement
                break;
        }
    }

    void MoveToward(Vector3 target, float speed, float stopDistance = 0.5f)
    {
        float dist = Vector3.Distance(transform.position, target);
        if (dist > stopDistance)
        {
            transform.position = Vector3.MoveTowards(
                transform.position, target, speed * Time.deltaTime);
        }
    }

    void MoveAway(Vector3 target, float speed)
    {
        Vector3 dir = (transform.position - target).normalized;
        transform.position += dir * speed * Time.deltaTime;
    }

    void OrbitAround(Vector3 center, float radius, float speed)
    {
        float angle = Time.time * speed * 0.5f + GetInstanceID() * 0.1f;
        Vector3 offset = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle)) * radius;
        transform.position = Vector3.Lerp(transform.position, center + offset, Time.deltaTime * 2f);
    }

    Vector3 GetGuardOffset()
    {
        float angle = GetInstanceID() * 0.7f; // Deterministic angle per NPC
        return new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle)) * 4f;
    }
}
