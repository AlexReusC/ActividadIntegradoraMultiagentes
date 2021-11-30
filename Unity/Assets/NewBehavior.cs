using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;


public class Constants
{

        public const float WAIT_TIME = 1.0f;
}

public static class JsonHelper
{
    public static T[] FromJson<T>(string json)
    {
        Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(json);
        return wrapper.Items;
    }

    public static string ToJson<T>(T[] array)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper);
    }

    public static string ToJson<T>(T[] array, bool prettyPrint)
    {
        Wrapper<T> wrapper = new Wrapper<T>();
        wrapper.Items = array;
        return JsonUtility.ToJson(wrapper, prettyPrint);
    }

    [System.Serializable]
    private class Wrapper<T>
    {
        public T[] Items;
    }
}

[System.Serializable]
class Agent
{
    public int x;
    public int y;
    public string typeAgent;

    public int condition;

    override public string ToString()
    {
        return "X: " + x + ", Y: " + y + ", typeAgent: " + typeAgent + ", condition: " + condition;
    }
}

public class NewBehavior : MonoBehaviour
{
    // Start is called before the first frame update
    public List<GameObject> agentCollection;
    public GameObject myBox, myRobot, myRobotBox, cube,
     pallet, pallet1, pallet2, pallet3, pallet4, pallet5;


    string simulationURL = null;
    private float timer = 0.0f;
    void Start()
    {
        for(int i = 0; i < 14; i++)
        {
            for(int j = 0; j < 14; j++)
            {
                Instantiate(cube, new Vector3(i, -1, j), Quaternion.identity);
            }
        }
        agentCollection = new List<GameObject>();
        StartCoroutine(ConnectToMesa());
    }

    IEnumerator ConnectToMesa()
    {
        WWWForm form = new WWWForm();

        using (UnityWebRequest www = UnityWebRequest.Post("http://localhost:5000/simulation", form))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                Debug.Log(www.error);
            }
            else
            {
                simulationURL = www.GetResponseHeader("Location");
                Debug.Log("Connected to simulation through Web API");
            }
        }
    }

    IEnumerator UpdatePositions()
    {
        using (UnityWebRequest www = UnityWebRequest.Get(simulationURL))
        {
            if (simulationURL != null)
            {
                cleanAgents();
                // Request and wait for the desired page.
                yield return www.SendWebRequest();

                Debug.Log(www.downloadHandler.text);
                Debug.Log("Data has been processed");
                Agent[] agents = JsonHelper.FromJson<Agent>(www.downloadHandler.text);

                for(int i = 0; i < agents.Length; i++){
                    if(agents[i].typeAgent == "Box"){
                        GameObject tmp = Instantiate(myBox, new Vector3(agents[i].x+0.5f, 0.3f, agents[i].y-0.5f), Quaternion.identity);
                        agentCollection.Add(tmp);
                    }
                    else if(agents[i].typeAgent == "Robot"){
                        if(agents[i].condition == 1){
                            GameObject tmp = Instantiate(myRobot, new Vector3(agents[i].x+0.5f, 0, agents[i].y-0.5f), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                        else if(agents[i].condition == 0){
                            GameObject tmp = Instantiate(myRobotBox, new Vector3(agents[i].x, 0, agents[i].y), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                    }
                    else if(agents[i].typeAgent == "Wall"){
                        GameObject tmp = Instantiate(cube, new Vector3(agents[i].x, 0, agents[i].y), Quaternion.identity);
                        agentCollection.Add(tmp);
                    }
                    else if(agents[i].typeAgent == "Pallet"){
                        if(agents[i].condition == 0){
                            GameObject tmp = Instantiate(pallet, new Vector3(agents[i].x+0.5f, 0, agents[i].y-0.5f), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                        else if(agents[i].condition == 1){
                            GameObject tmp = Instantiate(pallet1, new Vector3(agents[i].x+6.07f, 6.43f, agents[i].y+6.78f), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                        else if(agents[i].condition == 2){
                            GameObject tmp = Instantiate(pallet2, new Vector3(agents[i].x+6,6.41f, agents[i].y+6.62f), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                        else if(agents[i].condition == 3){
                            GameObject tmp = Instantiate(pallet3, new Vector3(agents[i].x+6, 6.41f, agents[i].y+6.62f), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                        else if(agents[i].condition == 4){
                            GameObject tmp = Instantiate(pallet4, new Vector3(agents[i].x-0.5f, 0, agents[i].y-2.0f), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                        else if(agents[i].condition == 5){
                            GameObject tmp = Instantiate(pallet5, new Vector3(agents[i].x-0.5f, 0, agents[i].y-2.0f), Quaternion.identity);
                            agentCollection.Add(tmp);
                        }
                    }
                }
            }
        }
    }

    void cleanAgents(){
        for(int i = 0; i < agentCollection.Count; i++){
            Destroy(agentCollection[i]);
        }
        agentCollection = new List<GameObject>();
    }


    // Update is called once per frame
    void Update()
    {
        timer += Time.deltaTime;
        if (timer > Constants.WAIT_TIME)
        {
            StartCoroutine(UpdatePositions());
            timer = timer - Constants.WAIT_TIME;
        }
    }
}
